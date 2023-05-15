# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=too-many-instance-attributes

from dataclasses import MISSING, asdict, dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import List, Literal, Optional, Union

import yaml

from azure.cli.core.azclierror import ValidationError
from azure.cli.core.util import is_guid
from azure.mgmt.core.tools import is_valid_resource_id


def _snake_to_camel(name: str):
    parts = name.split('_')
    return parts[0] + ''.join(word.title() for word in parts[1:])


def _camel_to_snake(name: str):
    return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')


def _validate_data_object(data_type: type, obj: dict, path: Path = None, parent_key: str = None):
    '''Validates a dict data object against a dataclass type.
    Ensures all required fields are present and that no invalid fields are present.'''

    flds = fields(data_type)
    all_fields = [_snake_to_camel(f.name) for f in flds]
    req_fields = [_snake_to_camel(f.name) for f in flds if f.default is MISSING]
    # opt_fields = [f.name for f in flds if f.default is not MISSING]

    key_prefix = f'{parent_key}.' if parent_key else ''

    name = f'{path}' if path else f'{data_type.__name__} object'

    for k in req_fields:
        if k not in obj:
            raise ValidationError(f'{name} is missing required property: {key_prefix}{k}')
        if not obj[k]:
            raise ValidationError(f'{name} is missing a value for required property: {key_prefix}{k}')
        # TODO: Validate types
    for k in obj:
        if k not in all_fields and k not in ['file', 'dir']:
            raise ValidationError(f'{name} contains an invalid property: {key_prefix}{k}')


def get_dict(instance):
    # TODO: shoul we filter False values?  How can we convert back to string lists for things like choco packages?
    return asdict(instance, dict_factory=lambda x: {_snake_to_camel(k): v for k, v in x
                                                    if v is not None and v is not False})


def has_only(instance, field_name: str) -> bool:
    if is_dataclass(instance):
        return not any(getattr(instance, f.name) for f in fields(instance) if f.name != field_name) \
            and getattr(instance, field_name, None) is not None
    elif isinstance(instance, dict):
        return not any(v for k, v in instance.items() if k != field_name) \
            and instance.get(field_name, None) is not None
    else:
        raise Exception(f'has_only() can only be used with dataclass or dict instances')


@dataclass
class Manifest:
    file: Path

    name: str
    version: str
    summary: str
    description: str
    runner: Literal['ARM', 'Terraform']  # str
    template_path: Union[str, Path]  # Path

    dir: Path = None

    def __init__(self, obj: dict, path: Path) -> None:
        if 'file' not in obj:
            obj['file'] = path

        _validate_data_object(Manifest, obj, path=path)

        for k, v in obj.items():
            setattr(self, _camel_to_snake(k), v)

        self.dir = path.parent
        self.template_path = path.parent / self.template_path
