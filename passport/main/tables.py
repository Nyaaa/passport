import django_tables2 as tables
from .models import Item
from django_tables2.utils import A


class ItemTable(tables.Table):
    edit = tables.LinkColumn('item_edit', args=[A('pk')], orderable=False, empty_values=())

    class Meta:
        model = Item
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped "}

    @staticmethod
    def render_edit():
        return 'Edit'
