import django_tables2 as tables
from .models import Item, Set, Series
from django_tables2.utils import A


def table_factory(_model, text: str):
    class Table(tables.Table):
        edit = tables.LinkColumn(f'{text}_edit', args=[A('pk')], orderable=False, empty_values=())
        delete = tables.LinkColumn(f'{text}_delete', args=[A('pk')], orderable=False, empty_values=())

        class Meta:
            model = _model
            template_name = "django_tables2/bootstrap5.html"
            attrs = {"class": "table table-striped "}

        @staticmethod
        def render_edit():
            return 'Edit'

        @staticmethod
        def render_delete():
            return 'Delete'

    return Table


class SetTable(tables.Table):
    edit = tables.LinkColumn('set_edit', args=[A('pk')], orderable=False, empty_values=())

    class Meta:
        model = Set
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped "}

    @staticmethod
    def render_edit():
        return 'Edit'

