from django.db import models
from django.utils import timezone


class DynamicTable(models.Model):
    table_name = models.CharField(max_length=255, null=True, unique=True)
    fields = models.JSONField()
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
