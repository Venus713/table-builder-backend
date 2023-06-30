from typing import List, Dict, Any
from django.apps import apps
from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import uuid

from .models import DynamicTable
from .serializers import DynamicTableSerializer
from .utils import compare_fields, get_model_field, create_dynamic_model


class TableAPIView(APIView):
    def post(self, request):
        fields: List[Dict[str, Any]] = request.data.get("fields", [])
        table_name: str = request.data.get(
            "table_name", f"dynamic_table_{uuid.uuid1()}")

        # Basic data validation
        if not isinstance(fields, list):
            raise ValidationError(
                "Fields must be a list of field definitions.")

        create_dynamic_model(table_name, fields)

        serializer = DynamicTableSerializer(
            data={"table_name": table_name, "fields": fields})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)

    def put(self, request, id):
        new_fields: List[Dict[str, Any]] = request.data.get("fields", [])

        dynamic_model = get_object_or_404(DynamicTable, pk=id)

        if not isinstance(new_fields, list):
            raise ValidationError(
                "New fields must be a list of field definitions.")

        try:
            model_class = apps.get_model("apis", dynamic_model.table_name)
        except Exception:
            return Response({"error": "Invalid table name"}, status=400)

        _, fields_to_add, fields_to_remove = compare_fields(
            dynamic_model.fields, new_fields)

        data: dict = {}

        with connection.schema_editor() as schema_editor:
            # Remove fields from the model_class
            for field in fields_to_remove:
                schema_editor.remove_field(
                    model_class, model_class._meta.get_field(field["name"]))

                local_fields = [
                    f for f in model_class._meta.local_fields if f.name != field["name"]]
                model_class._meta.local_fields = local_fields

            # Add new fields to the model_class
            for field in fields_to_add:
                field_name = field["name"]
                new_field = get_model_field(field["type"].lower())
                new_field.name = field_name
                new_field.attname = field_name
                new_field.column = field_name
                new_field.model = dynamic_model._meta.model
                new_field.concrete = True
                schema_editor.add_field(model_class, new_field)
                model_class._meta.local_fields.append(new_field)

            model_class._meta.fields = tuple(model_class._meta.local_fields)

            data.update({"fields": new_fields})

        serializer = DynamicTableSerializer(
            dynamic_model, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)


class TableRowAPIView(APIView):
    def post(self, request, id):
        data: Dict[str, Any] = request.data.get("data", {})

        dynamic_model = get_object_or_404(DynamicTable, pk=id)

        if not isinstance(data, dict):
            raise ValidationError(
                "the data must be a dict of field-value pair.")

        try:
            model_class = apps.get_model("apis", dynamic_model.table_name)
        except Exception:
            return Response({"error": "Invalid table name"}, status=400)

        row_instance = model_class()

        try:
            row_instance = model_class(**data)
            row_instance.save()
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({"message": "Row added successfully"}, status=201)

    def get(self, request, id):
        dynamic_model = get_object_or_404(DynamicTable, pk=id)

        try:
            model_class = apps.get_model("apis", dynamic_model.table_name)
        except Exception:
            return Response({"error": "Invalid table name"}, status=400)

        rows = model_class.objects.all()

        data: list = []
        for row in rows:
            row_data: dict = {}
            for field in row._meta.fields:
                row_data[field.name] = getattr(row, field.name)
            data.append(row_data)

        return Response(data, status=200)
