import django_tables2 as tables
from .models import Set, Order
from django_tables2.utils import A
from django.utils.html import format_html


class MetaColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        self.action = kwargs.pop('action')
        super().__init__(*args, **kwargs)
        self.orderable = False
        self.exclude_from_export = True
        self.empty_values = ()
        self.attrs = {'td': {'class': 'text-center'},
                      'th': {'style': 'width:1%'},
                      }

    def render(self, value):
        if self.action == 'Delete':
            return format_html('<i class="fa-regular fa-trash-can"></i>')
        elif self.action == 'Edit':
            return format_html('<i class="fa-regular fa-pen-to-square"></i>')
        else:
            return format_html('<i class="fa-regular fa-file-lines"></i>')


def table_factory(_model, text: str):
    class Table(tables.Table):
        edit = MetaColumn(linkify=(f'{text}_edit', [A('pk')]), action='Edit')
        delete = MetaColumn(linkify=(f'{text}_delete', [A('pk')]), action='Delete')

        class Meta:
            model = _model
            template_name = 'django_tables2/bootstrap5.html'
            attrs = {'class': 'table table-striped'}
            sequence = ('...', 'edit', 'delete')

    return Table


class SetTable(tables.Table):
    view = MetaColumn(linkify=('set_detail', [A('pk')]), action='View')
    edit = MetaColumn(linkify=('set_edit', [A('pk')]), action='Edit')
    delete = MetaColumn(linkify=('set_delete', [A('pk')]), action='Delete')
    # TODO: sorting
    assigned_to = tables.Column(accessor='assigned_to.distributor', orderable=False)
    date = tables.DateTimeColumn(accessor='assigned_to.date', format='Y-m-d', orderable=False)
    recipient = tables.Column(accessor='assigned_to.recipient', orderable=False)
    city = tables.Column(accessor='assigned_to.city', orderable=False)
    document = tables.Column(accessor='assigned_to.document', orderable=False)

    class Meta:
        model = Set
        template_name = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-striped'}
        sequence = ('...', 'view', 'edit', 'delete')


class OrderTable(tables.Table):
    view = MetaColumn(linkify=('order_detail', [A('pk')]), action='View')
    edit = MetaColumn(linkify=('order_edit', [A('pk')]), action='Edit')
    delete = MetaColumn(linkify=('order_delete', [A('pk')]), action='Delete')
    date = tables.DateTimeColumn(format='Y-m-d')
    sets = tables.ManyToManyColumn()

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-striped'}
        sequence = ('...', 'view', 'edit', 'delete')
        exclude = ('id',)
