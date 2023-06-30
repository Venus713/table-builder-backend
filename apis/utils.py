from typing import Union, List, Tuple, Dict, Any
from django.apps import apps
from django.db import models, connection
from rest_framework.exceptions import ValidationError


def get_model_field(field_type: str) -> Union[models.CharField, models.IntegerField, models.BooleanField]:
    if field_type == "string":
        new_field = models.CharField(max_length=255, null=True)
    elif field_type == "number":
        new_field = models.IntegerField(blank=True, null=True)
    elif field_type == "boolean":
        new_field = models.BooleanField(default=False)
    else:
        raise ValidationError(
            f"Unsupported field type: {field_type}")
    return new_field


def create_dynamic_model(table_name: str, fields: List[dict]) -> models.base.ModelBase:
    # Dynamically create a new model for the given table_name and fields
    meta = type('Meta', (), {'app_label': "apis"})
    attrs = {'__module__': __name__, 'Meta': meta}

    for field in fields:
        field_name: str = field["name"]
        try:
            field_type: str = get_model_field(field["type"].lower())
        except KeyError:
            raise ValidationError(
                f"Unsupported field type: {field['type']}")

        attrs[field_name] = field_type

    dynamic_model = type(table_name, (models.Model,), attrs)

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(dynamic_model)

    apps.register_model(app_label='apis', model=dynamic_model)

    return dynamic_model


def compare_fields(org_fields: List[dict], new_fields: List[dict]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    org_dict = {d['name']: d['type'] for d in org_fields}
    new_dict = {d['name']: d['type'] for d in new_fields}

    same_fields: List[Dict[str, Any]] = []
    add_fields: List[Dict[str, Any]] = []
    remove_fields: List[Dict[str, Any]] = []

    # Check for same items
    for name, type_new in new_dict.items():
        if name in org_dict:
            type_org = org_dict[name]
            if type_new == type_org:
                same_fields.append({'name': name, 'type': type_new})
            else:
                add_fields.append({'name': name, 'type': type_new})
                remove_fields.append({'name': name, 'type': type_org})

    # Check for add items
    for name, type_new in new_dict.items():
        if name not in org_dict:
            add_fields.append({'name': name, 'type': type_new})

    # Check for delete items
    for name, type_org in org_dict.items():
        if name not in new_dict:
            remove_fields.append({'name': name, 'type': type_org})

    return same_fields, add_fields, remove_fields
