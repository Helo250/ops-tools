# ops-tools
## 介绍
> - 提供运维工具，包含变更记录留存，消息的定时通知，数据自定义加密，账号加密管理，支持数据批量导入到处
> - 支持用户组或特定成员的权限赋予过滤有效数据
## 框架
> - restful风格， 使用Tornado，封装RestAPI对象，实现对前端提供api，MongoDB用作数据存储
> - 采用多进程方式与异步结合的方式，使得web server 和 period server相互独立，提高多核利用率
