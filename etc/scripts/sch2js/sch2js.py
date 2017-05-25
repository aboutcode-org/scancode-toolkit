# The MIT License (MIT)
#
# Copyright (c) 2014 Alex Kessinger
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# based on download_url: https://raw.githubusercontent.com/boblannon-picwell/jsonschematics/ac24246459c51ad730d008a4e97c2f16a115dd2c/jsonschematics/__init__.py
# and modified

"""
Convert a schematics model to a JSON schema.

To use:

from packagedcode.models import *
import json
from sch2js import to_jsonschema
models = [Package, Repository, AssertedLicense, Party, Dependency, RelatedPackage]
for model in models:
  jsc = to_jsonschema(model)
  with open('doc/' + model.__name__ + '-json-schema.json', 'w') as o:
    json.dump(jsc, o, indent=2)
"""

from collections import OrderedDict

from six import iteritems

from schematics.types.base import BaseType
from schematics.types.compound import ListType
from schematics.types.compound import ModelType


__version__ = '1.0.1.patch'


SCHEMATIC_TYPE_TO_JSON_TYPE = {
    'NumberType': 'number',
    'IntType': 'integer',
    'LongType': 'integer',
    'FloatType': 'number',
    'DecimalType': 'number',
    'BooleanType': 'boolean',
    'BaseType': 'object'
}

# Schema Serialization

# Parameters for serialization to JSONSchema
schema_kwargs_to_schematics = {
    'maxLength': 'max_length',
    'minLength': 'min_length',
    'pattern': 'regex',
    'minimum': 'min_value',
    'maximum': 'max_value',
    'enum': 'choices'
}


def jsonschema_for_single_field(field_instance):
    """
    Return a mapping for the schema of a single field.
    """
    field_schema = OrderedDict()

    field_schema['type'] = SCHEMATIC_TYPE_TO_JSON_TYPE.get(
        field_instance.__class__.__name__, 'string')

    if hasattr(field_instance, 'metadata'):
        field_schema['title'] = field_instance.metadata.get('label', '')
        field_schema['description'] = field_instance.metadata.get('description', '')

    for js_key, schematic_key in iteritems(schema_kwargs_to_schematics):
        value = getattr(field_instance, schematic_key, None)
        if value is not None:
            field_schema[js_key] = value

    return field_schema


def jsonschema_for_fields(model):
    """
    Return a mapping for the schema of a collection of fields.
    """
    properties = OrderedDict()
    required = []
    for field_name, field_instance in iteritems(model.fields):
        serialized_name = getattr(field_instance, 'serialized_name', None) or field_name

        if isinstance(field_instance, ModelType):
            node = jsonschema_for_model(field_instance.model_class)

        elif isinstance(field_instance, ListType):
            try:
                node = jsonschema_for_model(field_instance.model_class, 'array')
                if hasattr(field_instance, 'metadata'):
                    _node = OrderedDict()
                    _node['type'] = node.pop('type')
                    _node['title'] = field_instance.metadata.get('label', '')
                    _node['description'] = field_instance.metadata.get('description', '')
                    _node.update(node)
                    node = _node
            except AttributeError:
                field_schema = jsonschema_for_single_field(field_instance.field)
                node = OrderedDict()
                node['type'] = 'array'
                if hasattr(field_instance, 'metadata'):
                    node['title'] = field_instance.metadata.get('label', '')
                    node['description'] = field_instance.metadata.get('description', '')
                node['items'] = field_schema

        # Convert field as single model
        elif isinstance(field_instance, BaseType):
            node = jsonschema_for_single_field(field_instance)

        if getattr(field_instance, 'required', False):
            required.append(serialized_name)
            properties[serialized_name] = node
        else:
            properties[serialized_name] = {
                'oneOf': [
                    node,
                    {'type': 'null'},
                ]
            }

    return properties, required


def jsonschema_for_model(model, _type='object'):
    """
    Return a mapping for the schema of a model field.
    """

    properties, required = jsonschema_for_fields(model)

    if hasattr(model, 'metadata'):
        schema_title = model.metadata.get('label', '')
        schema_description = model.metadata.get('description', '')
    else:
        schema_title = ''
        schema_description = ''

    schema = OrderedDict([
        ('type', 'object'),
        ('title', schema_title),
        ('description', schema_description),
    ])

    if required:
        schema['required'] = required

    if hasattr(model, '_schema_order'):
        ordered_properties = [(i, properties.pop(i)) for i in model._schema_order]
        schema['properties'] = OrderedDict(ordered_properties)
    else:
        schema['properties'] = properties

    if _type == 'array':
        schema = OrderedDict([
            ('type', 'array'),
            ('items', schema),
        ])

    return schema


def to_jsonschema(model, **kwargs):
    """
    Return a a JSON schema mapping for the `model` class.
    """
    schema_id = kwargs.pop('schema_id', '')
    jsonschema = OrderedDict([
        ('$schema', 'http://json-schema.org/draft-04/schema#'),
        ('id', schema_id)
    ])
    jsonschema.update(jsonschema_for_model(model))
    return jsonschema
