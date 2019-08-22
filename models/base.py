# -*- coding: utf-8 -*-
# Filename: base
# Author: brayton
# Datetime: 2019-Jul-17 4:58 PM

from motorengine.metaclasses import DocumentMetaClass
from motorengine.document import BaseDocument as _BaseDocument
from motorengine.fields import ListField, DateTimeField
from motorengine.fields.base_field import BaseField
from motorengine.fields import ReferenceField as _ReferenceField, EmbeddedDocumentField as _EmbeddedDocumentField
import weakref
from inspect import isawaitable
from bson.objectid import ObjectId
from ujson import dumps, loads
from tornado.log import app_log

from handler.exceptions import ValidationError
from utils import uncapitalize, snake2camel

allowed_config = {'verbose', 'writable', 'readable'}


class ReferenceField(_ReferenceField):
    def validate(self, value):
        if not isinstance(self.reference_type, type) or not issubclass(self.reference_type, BaseDocument):
            raise ValueError(
                "The field 'reference_document_type' argument must be a subclass of BaseDocument, not '%s'." % (
                    str(self.reference_type)
                )
            )
        if value is not None and not isinstance(value, (self.reference_type, ObjectId)):
            return False

        return value is None or isinstance(value, ObjectId) or (hasattr(value, '_id') and value._id is not None)

    def get_value(self, value):
        print('...........')
        return value

    def to_son(self, value):
        if value is None:
            return None

        if isinstance(value, ObjectId):
            return value

        return ObjectId(value)

    def from_son(self, value):
        value = self.reference_type.objects.get(id=value)
        return value


class EmbeddedDocumentField(_EmbeddedDocumentField):
    def validate(self, value):
        if not isinstance(self.embedded_type, type) or not issubclass(self.embedded_type, BaseDocument):
            raise ValueError(
                "The field 'embedded_document_type' argument must be a subclass of BaseDocument, not '%s'." %
                str(self.embedded_type)
            )

        if value is None:
            return True

        if value is not None and not isinstance(value, self.embedded_type):
            return False

        return value.validate()


class JsonField(BaseField):
    def validate(self, value):
        try:
            dumps(value)
            return True
        except:
            return False

    def to_son(self, value):
        return dumps(value)

    def from_son(self, value):
        if isinstance(value, dict):
            return value
        return loads(value)

#
# class _DatetimeField(DateTimeField):
#     def to_son(self, value):
#


class BaseDocumentMetaClass(DocumentMetaClass):
    def __new__(kls, name, bases, attrs):
        cls = super().__new__(kls, name, bases, attrs)
        meta = cls.process_meta(bases)
        setattr(cls, 'meta', meta)
        return cls

    def _gen_verbose_name(cls, field_name):
        return f''

    def __build_default_fields_config(cls, cls_verbose_name):
        _dict = dict()
        for name, field in cls._fields.items():
            _dict[name] = {
                'verbose': f'{cls_verbose_name}{snake2camel(field.db_field)}',
                'writable': True,
                'readable': True,
                'field': field
            }
        return _dict

    def process_meta(cls, bases):
        # if not hasattr(cls, 'Meta'):
        #     raise TypeError('The `Meta` class is required')
        verbose_name = getattr(cls.Meta, 'verbose_name', None)
        fields_map = getattr(cls.Meta, 'fields_map', {})
        # del cls.Meta
        if not verbose_name:
            verbose_name = uncapitalize(cls.__name__)
        _meta = type('meta', (), {
            'fields_map': cls.__build_default_fields_config(verbose_name),
            'verbose_name': verbose_name
        })
        # for base in sorted(cls._get_bases(bases), reverse=True):
        #     if hasattr(base, 'meta'):
        #         _meta = base.meta

        if not isinstance(fields_map, dict):
            raise TypeError('Invalid type attribute: fields_map, it is expected as dictionary!')
        for name, config in fields_map.items():
            if name not in cls._fields:
                raise TypeError(f'Invalid field: {name}')
            if set(config) - allowed_config:
                raise TypeError(f'Invalid config, only follow fields {allowed_config} is accessed')
            getattr(_meta, name, {}).update(config)
        return _meta


class BaseDocument(_BaseDocument, metaclass=BaseDocumentMetaClass):

    class Meta:
        fields_map = dict()
        verbose_name = None

    @classmethod
    def get_field_by_verbose_name(cls, name):
        for field_name, field in list(cls.meta.fields_map.items()):
            if field['verbose'] == name:
                return field['field']
        return cls.get_field_by_db_name(name)

    def to_dict(self):
        data = dict()
        fields_map = getattr(self.meta, 'fields_map', {})

        for name, field in list(self._fields.items()):
            value = self.get_field_value(name)
            if field.sparse and value is None:
                continue
            value = field.from_son(value)
            data[fields_map[field.db_field]['verbose']] = value
        data['id'] = self._id

        return data

    @classmethod
    def validate_values(cls, dic, allow_cover=True):
        validated = {}
        for _id in ('id', '_id', 'Id', f'{uncapitalize(cls.meta.verbose_name)}Id'):
            _object_id = dic.pop(_id, None)
            if _object_id:
                break

        for name, value in list(dic.items()):
            field = cls.get_field_by_verbose_name(name)
            if not field:
                raise ValidationError('Unknown data: {"%s": "%s"}' % (name, value))
            # if isinstance(field, ListField):
            #     value = list(map(dumps, value))
            try:
                validated[field.name] = field.to_son(value)
            except Exception as e:
                app_log.error('>>>>>>>>>>>>>>>>>>>>..%s' % e)
        validated['_id'] = _object_id if allow_cover else None
        return validated

    @classmethod
    def from_dict(cls, dic, _is_partly_loaded=False, _reference_loaded_fields=None):
        try:
            validated_data = cls.validate_values(dic, allow_cover=False)
        except ValidationError as e:
            raise e
        except Exception as e:
            app_log.error(f'Validate value error: {e}, data: {dic}')
            raise

        return cls(
            _is_partly_loaded=_is_partly_loaded,
            _reference_loaded_fields=_reference_loaded_fields,
            **validated_data
        )

    @classmethod
    def update(cls, instance, validated_data):
        validated_data.pop('_id', None)
        for field_name, value in validated_data.items():
            setattr(instance, field_name, value)
        return instance

