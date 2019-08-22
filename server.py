#!/usr/bin/env python
# coding:utf-8

from handler.patch import patch_all
import os
patch_all()

from tornado import ioloop
import tornado.netutil
import tornado.options
import tornado
from tornado.options import define, options, parse_command_line
from motorengine.connection import register_connection, DEFAULT_CONNECTION_NAME, connect
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
# from tornado.process import fork_processes
from tornado import netutil
import tempfile
import fcntl
import signal
import errno

from settings import MONGODB
from tornado.ioloop import PeriodicCallback
from pymongo.errors import ServerSelectionTimeoutError
import time
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure
from multiprocessing import Process
from setproctitle import setproctitle
import random
import threading
import sys
import logging
import json
from datetime import datetime
import select

_logger = logging.getLogger('service')


define("port", group='Webserver', type=int, default=8500, help="Run on the given port")
define("addr", group='Webserver', type=str, default='0.0.0.0', help="Run on the given addr")
define("subpath", group='Webserver', type=str, default="/api", help="Url subpath (such as /nebula)")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def empty_pipe(fd):
    try:
        while os.read(fd, 1):
            pass
    except OSError as e:
        if e.errno not in [errno.EAGAIN]:
            raise


class Worker(object):

    _waiting = {}

    def __init__(self, multi):
        self.multi = multi
        self.watchdog_time = time.time()
        self.watchdog_pipe = multi.pipe_new()
        self.eintr_pipe = multi.pipe_new()
        self.wakeup_fd_r, self.wakeup_fd_w = self.eintr_pipe
        self.watchdog_timeout = multi.timeout
        self.pid = os.getpid()
        self.alive = True
        self._io_loop = None
        self.returncode = None

    def set_proctitle(self, title=''):
        setproctitle(f'Tools: {self.__class__.__name__}-{self.pid}-{title}')

    def close(self):
        os.close(self.watchdog_pipe[0])
        os.close(self.watchdog_pipe[1])
        os.close(self.watchdog_pipe[0])
        os.close(self.watchdog_pipe[1])

    def signal_handler(self, sig, frame):
        self.alive = False
        self.io_loop.add_callback_from_signal(self._cleanup)

    def _cleanup(self):
        self.io_loop.stop()

    @property
    def io_loop(self):
        if not self._io_loop:
            self._io_loop = IOLoop()
        return self._io_loop

    def sleep(self):
        pass

    def process_work(self):
        pass

    def start(self):
        self.pid = os.getpid()
        self.set_proctitle()
        print(f'Worker {self.__class__.__name__} {self.pid} alive')
        random.seed()
        # if self.multi.socket:
        #     flags = fcntl.fcntl(self.multi.socket, fcntl.F_GETFD) | fcntl.FD_CLOEXEC
        #     fcntl.fcntl(self.multi.socket, fcntl.F_SETFD, flags)
        #     self.multi.socket.setblocking(0)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGCHLD, self.signal_handler)
        signal.set_wakeup_fd(self.wakeup_fd_w)

    def stop(self):
        pass

    def run(self):
        try:
            self.start()
            # t = threading.Thread(name=f'Worker {self.__class__.__name__} ({self.pid}) work threaded', target=self._runloop)
            # t.start()
            # t.join()
            print(f'Worker {self.__class__.__name__} ({self.pid}) exiting.')
            # self.stop()
        except Exception as e:
            print(f'Exception: {e}')
            sys.exit(1)

    def _runloop(self):
        try:
            while self.alive:
                self.multi.pipe_ping(self.watchdog_pipe)
                self.sleep()
                if not self.alive:
                    break
                self.process_work()
        except Exception as e:
            print(f'Exception: {e}')
            sys.exit(1)


class WorkerHTTP(Worker):
    def start(self):
        Worker.start(self)
        self.io_loop.make_current()
        server = HTTPServer(self.multi.app)
        server.add_sockets(self.multi.sockets)
        self.io_loop.start()


def dumps(fn):
    def wrapper(self, *args, **kwargs):
        filepath = '/tmp/tools-cron-worker(%s)' % self.pid
        with open('/tmp/hello_schedule', 'a+') as f:
            result = fn(self, *args, **kwargs)
        return result
    return wrapper

class WorkerCron(Worker):
    @dumps
    def _schedule(self):
        msgs = list()
        for msg in self.db.Message.find({
            'is_active': True, 'status': 'to_send',
            'sent_at': {'$gte': datetime.now()}
        }):
            msgs.append(msg)

    @staticmethod
    async def test_schedule(*args, **kwargs):
        from models.message import Message
        await Message.ir_cron()
        # msgs = await Message.objects.find_all()
        # print(msgs[0].to_dict())
        with open('/tmp/hello_schedule', 'a+') as f:
            f.write(f'test－{time.time()} \n')


    def start(self):
        os.nice(10)
        Worker.start(self)
        self.db = MongoClient('mongodb://localhost:27017').test
        self.schedule = PeriodicCallback(self._schedule, 5000)
        for sock in self.multi.sockets:
            sock.close()
        self.io_loop.make_current()
        self.schedule.start()
        self.io_loop.start()

        # self.io_loop.
        #
        # schedule = PeriodicCallback(test_schedule, 5000)
        # try:
        #     self.io_loop.make_current()
        #     from models.message import Message
        #
        # schedule.start()
        #     # while True:
        #     #     self.db.
        #     self.io_loop.run_in_executor(None, Message.ir_cron, Message)


class Service(object):
    def __init__(self, app):
        self._initialize()
        self.app = app
        self.pid = os.getpid()
        self._cron_pid = None
        self.workers_http = {}
        self.workers_cron = {}
        self.workers = {}
        self.queue = []
        self.generation = 0
        self.population = 2
        self.max_crons = 0
        self.timeout = 5
        self.beat = 4

    def _initialize(self):
        self.register_db(MONGODB.name, host=MONGODB.host, port=MONGODB.port)

    def pipe_new(self):
        pipe = os.pipe()
        for fd in pipe:
            # non_blocking
            flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
            fcntl.fcntl(fd, fcntl.F_SETFL, flags)
            # close_on_exec
            flags = fcntl.fcntl(fd, fcntl.F_GETFD) | fcntl.FD_CLOEXEC
            fcntl.fcntl(fd, fcntl.F_SETFD, flags)
        return pipe

    def pipe_ping(self, pipe):
        try:
            os.write(pipe[1], b'.')
        except IOError as e:
            if e.errno not in [errno.EAGAIN, errno.EINTR]:
                raise

    def signal_handler(self, sig, frame):
        if len(self.queue) < 5 or sig == signal.SIGCHLD:
            self.queue.append(sig)
            self.pipe_ping(self.pipe)
        else:
            pass
            # _logger.warn("Dropping signal: %s", sig)

    def process_signals(self):
        while len(self.queue):
            sig = self.queue.pop(0)
            if sig in [signal.SIGINT, signal.SIGTERM]:
                raise KeyboardInterrupt
            elif sig == signal.SIGHUP:
                # restart on kill -HUP
                raise KeyboardInterrupt

    def process_zombie(self):
        # reap dead workers
        while True:
            try:
                wpid, status = os.waitpid(-1, os.WNOHANG)
                if not wpid:
                    break
                if (status >> 8) == 3:
                    msg = "Critial worker error (%s)"
                    print(msg, wpid)
                    raise Exception(msg % wpid)
                self.worker_pop(wpid)
            except OSError as e:
                if e.errno == errno.ECHILD:
                    break
                raise

    def sleep(self):
        try:
            # map of fd -> worker
            fds = {w.watchdog_pipe[0]: w for w in self.workers.values()}
            fd_in = list(fds) + [self.pipe[0]]
            # check for ping or internal wakeups
            ready = select.select(fd_in, [], [], self.beat)
            # update worker watchdogs
            for fd in ready[0]:
                if fd in fds:
                    fds[fd].watchdog_time = time.time()
                empty_pipe(fd)
        except select.error as e:
            if e.args[0] not in [errno.EINTR]:
                raise

    @property
    def support_unix_socket(self):
        return os.name == 'posix'

    def process_spawn(self):
        while len(self.workers_http) < self.population:
            self.worker_spawn(WorkerHTTP, self.workers_http)
        while len(self.workers_cron) < self.max_crons:
            self.worker_spawn(WorkerCron, self.workers_cron)

    def worker_spawn(self, klass, workers_registry):
        self.generation += 1
        worker = klass(self)
        pid = os.fork()
        if pid != 0:
            worker.pid = pid
            self.workers[pid] = worker
            workers_registry[pid] = worker
            return worker
        else:
            worker.run()
            sys.exit(0)

    def worker_pop(self, pid):
        if pid in self.workers:
            print(f'Now kill worker {pid}')
            try:
                self.workers_http.pop(pid, None)
                self.workers_cron.pop(pid, None)
                w = self.workers.pop(pid)
                w.close()
            except OSError:
                return
            print(f'Close worker {w} successfully!')

    def worker_kill(self, pid, sig):
        try:
            os.kill(pid, sig)
        except OSError as e:
            if e.errno == errno.ESRCH:
                self.worker_pop(pid)

    def build_sockets(self, unix_socket=False):
        print('main pid', os.getpid())
        if unix_socket and self.support_unix_socket:
            self.tmpfile = tempfile.mkdtemp()
            socket_file = os.path.join(self.tmpfile, 'http.sock')
            sockets = [netutil.bind_unix_socket(socket_file)]
        else:
            sockets = netutil.bind_sockets(address=options.addr, port=options.port)
            print(f'>>>>>>the sockets is {sockets}')
        return sockets

    def register_db(self, db_name, **config):
        def pre_connect():
            test_config = dict(
                **config,
                serverselectiontimeoutms=500
            )
            try:
                # The ismaster command is cheap and does not require auth.
                MongoClient(**test_config).admin.command('ismaster')
                return True
            except ConnectionFailure:
                return False

        if not pre_connect():
            raise Exception('The mongodb deamon is down or the configure is error!')
        else:
            register_connection(db_name, DEFAULT_CONNECTION_NAME, **config)
            # connect(db_name, DEFAULT_CONNECTION_NAME, **config)

    def start(self, unix_socket=False):
        self.pipe = self.pipe_new()

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGHUP, self.signal_handler)
        signal.signal(signal.SIGCHLD, self.signal_handler)
        signal.signal(signal.SIGTTIN, self.signal_handler)
        signal.signal(signal.SIGTTOU, self.signal_handler)

        self.sockets = self.build_sockets(unix_socket)

    def run(self):
        self.start(False)

        print(f'Start service')
        while True:
            try:
                self.process_signals()
                self.process_zombie()
                self.process_spawn()
                self.sleep()
            except KeyboardInterrupt:
                print('Stop for keyboard interrupt!')
                self.stop()
                break
            except Exception as e:
                print(f'Error: {e}')
                self.stop(False)
                return -1

    def stop(self, graceful=True):

        if graceful:
            print('Stop gracefully')
            limit = time.time() + self.timeout
            for pid in self.workers:
                self.worker_kill(pid, signal.SIGINT)
            while self.workers and time.time() < limit:
                try:
                    self.process_signals()
                except KeyboardInterrupt:
                    break
                self.process_zombie()
                time.sleep(1)
        else:
            print('Stop forcefully')
        for pid in self.workers:
            self.worker_kill(pid, signal.SIGTERM)
        if self.sockets:
            for socket in self.sockets:
                socket.close()
            # map(lambda socket: socket.close(), self.sockets)
        print('stop all workers')



if __name__ == '__main__':
    from application import app
    service = Service(app)
    service.run()





# define("port", group='Webserver', type=int, default=8500, help="Run on the given port")
# define("subpath", group='Webserver', type=str, default="/api", help="Url subpath (such as /nebula)")
# define('unix_socket', group='Webserver', default=None, help='Path to unix socket to bind')
#
#
# def main():
#     options.logging = None
#     parse_command_line()
#     options.subpath = options.subpath.strip('/')
#     if options.subpath:
#         options.subpath = '/' + options.subpath
#
#     # Connect to mongodb
#     io_loop = ioloop.IOLoop.instance()
#     try:
#         print(connect(MONGODB.NAME, host=MONGODB.HOST, port=MONGODB.PORT, io_loop=io_loop))
#     except Exception as e:
#         print(f'>>>>>>MONGODB ERROR: {e}')
#     # Star application
#     from application import app
#
#     if options.unix_socket:
#         server = tornado.httpserver.HTTPServer(app)
#         socket = tornado.netutil.bind_unix_socket(options.unix_socket, 0o666)
#         server.add_socket(socket)
#         print('Server is running at %s' % options.unix_socket)
#         print('Quit the server with Control-C')
#
#     else:
#         http_server = tornado.httpserver.HTTPServer(app)
#         http_server.listen(options.port)
#         print('Server is running at http://127.0.0.1:%s%s' % (options.port, options.subpath))
#         print('Quit the server with Control-C')
#
#     io_loop.start()
#
#
# if __name__ == "__main__":
#     main()
