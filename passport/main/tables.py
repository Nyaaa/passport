import django_tables2 as tables
from .models import Item


class ItemTable(tables.Table):
    class Meta:
        model = Item
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped "}
