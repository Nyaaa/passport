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
    # TODO: sorting
    assigned_to = tables.Column(accessor='assigned_to.distributor', orderable=False)
    date = tables.DateTimeColumn(accessor='assigned_to.date', format='Y-m-d', orderable=False)
    recipient = tables.Column(accessor='assigned_to.recipient', orderable=False)
    city = tables.Column(accessor='assigned_to.city', orderable=False)
    document = tables.Column(accessor='assigned_to.document', orderable=False)

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
    sets = tables.ManyToManyColumn()

    class Meta:
        model = Order
        template_name = "django_tables2/bootstrap5.html"
        attrs = {"class": "table table-striped "}
        sequence = ('...', 'view', 'edit', 'delete')



