import django_tables2 as tables
from .models import Set, Order
from django_tables2.utils import A


def table_factory(_model, text: str):
    class Table(tables.Table):
        edit = tables.LinkColumn(f'{text}_edit', args=[A('pk')], orderable=False, empty_values=(), text='Edit')
        delete = tables.LinkColumn(f'{text}_delete', args=[A('pk')], orderable=False, empty_values=(), text='Delete')

        class Meta:
            model = _model
            template_name = "django_tables2/bootstrap5.html"
            attrs = {"class": "table table-striped "}
            sequence = ('...', 'edit', 'delete')

    return Table


class SetTable(tables.Table):
    view = tables.LinkColumn('set_detail', args=[A('pk')], orderable=False, empty_values=(), text='View')
    edit = tables.LinkColumn('set_edit', args=[A('pk')], orderable=False, empty_values=(), text='Edit')
    delete = tables.LinkColumn(f'set_delete', args=[A('pk')], orderable=False, empty_values=(), text='Delete')

    class Meta:
        model = Set
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped "}
        sequence = ('...', 'view', 'edit', 'delete')


class OrderTable(tables.Table):
    view = tables.LinkColumn('order_detail', args=[A('pk')], orderable=False, empty_values=(), text='View')
    edit = tables.LinkColumn('order_edit', args=[A('pk')], orderable=False, empty_values=(), text='Edit')
    delete = tables.LinkColumn(f'order_delete', args=[A('pk')], orderable=False, empty_values=(), text='Delete')
    date = tables.DateTimeColumn(format='Y-m-d')

    class Meta:
        model = Order
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped "}
        sequence = ('...', 'view', 'edit', 'delete')



