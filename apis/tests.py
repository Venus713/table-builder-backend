from django.urls import reverse
from django.test import TestCase
from rest_framework import status

from .models import DynamicTable


class TableAPIViewTests(TestCase):
    def setUp(self):
        url = reverse('table-create')
        self.initial_data = {
            'fields': [
                {'name': 'field1', 'type': 'string'},
                {'name': 'field2', 'type': 'number'},
                {'name': 'field3', 'type': 'boolean'}
            ],
            'table_name': 'test_table'
        }
        response = self.client.post(
            url, self.initial_data, content_type='application/json')
        self.id = response.data.get('id')

    def test_create_dynamic_table(self):
        url = reverse('table-create')
        data = {
            'fields': [
                {'name': 'field1', 'type': 'string'},
                {'name': 'field2', 'type': 'number'},
                {'name': 'field3', 'type': 'boolean'}
            ],
            'table_name': 'test_table_1'
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DynamicTable.objects.count(), 2)
        self.assertEqual(
            DynamicTable.objects.get(id=2).table_name, data['table_name'])
        self.assertEqual(
            DynamicTable.objects.get(id=2).fields, data['fields'])

    def test_create_dynamic_table_invalid_fields(self):
        url = reverse('table-create')
        data = {
            'fields': 'invalid_fields',
            'table_name': 'test_table'
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_dynamic_table(self):
        url = reverse('table-update', args=[self.id])
        update_data = {
            'fields': [
                {'name': 'field1', 'type': 'string'},
                {'name': 'field3', 'type': 'string'},
                {'name': 'field5', 'type': 'number'},
                {'name': 'field6', 'type': 'boolean'}
            ]
        }
        response = self.client.put(
            url, update_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(
            DynamicTable.objects.get().fields, update_data['fields'])

    def test_update_dynamic_table_invalid_fields(self):
        url = reverse('table-update', args=[self.id])
        update_data = {
            'fields': [
                {'name': 'field1', 'type': 'CharField'},
            ]
        }
        response = self.client.put(
            url, update_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TableRowAPIViewTests(TestCase):
    def setUp(self):
        url = reverse('table-create')
        self.initial_data = {
            'fields': [
                {'name': 'field1', 'type': 'string'},
                {'name': 'field2', 'type': 'number'},
                {'name': 'field3', 'type': 'boolean'}
            ],
            'table_name': 'test_table'
        }
        response = self.client.post(
            url, self.initial_data, content_type='application/json')
        self.id = response.data.get('id')

    def test_create_table_row(self):
        url = reverse('table-row-create', args=[self.id])
        data = {'data': {'field1': 'value1', 'field2': 10, 'field3': True}}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'message': 'Row added successfully'})

    def test_create_table_row_invalid_data(self):
        url = reverse('table-row-create', args=[self.id])
        data = {'data': 'invalid_data'}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_table_rows(self):
        url = reverse('table-row-list', args=[self.id])
        self.client.post(
            url, {'data': {'field1': 'value1', 'field2': 10, 'field3': True}}, content_type='application/json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['field1'], 'value1')
        self.assertEqual(response.data[0]['field2'], 10)
        self.assertEqual(response.data[0]['field3'], True)

    def test_get_table_rows_invalid_table(self):
        url = reverse('table-row-list', args=[1000])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
