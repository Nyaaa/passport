import django_tables2 as tables
from .models import Set, Order
from django.utils.html import format_html


class MetaColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False
        self.exclude_from_export = True
        self.empty_values = ()
        self.verbose_name = ''
        self.attrs = {'td': {'class': 'text-center'}}


class BaseMeta:
    model = None
    template_name = 'django_tables2/bootstrap5.html'
    attrs = {'class': 'table table-striped'}
    sequence = ('...', 'view', 'edit')


def table_factory(_model):
    """
    Create base table class with extra columns (view, edit, delete links)
    Args:
        _model (Model): Django model

    Returns:
        tables.Table
    """
    class Table(tables.Table):
        view = MetaColumn()
        edit = MetaColumn()

        def __init__(self, *args, **kwargs):
            """
            Get request from CommonListView to make urls with query string
            Args:
                **kwargs (): request
            """
            self.request = kwargs.pop("request")
            super().__init__(*args, **kwargs)
            self.q_str = self.request.GET.urlencode()

        def render_edit(self, record):
            return format_html(f'<a href="{record.pk}/edit/?{self.q_str}">'
                               '<i class="fa-regular fa-pen-to-square"></i></a>')

        def render_view(self, record):
            return format_html(f'<a href="{record.pk}/?{self.q_str}">'
                               '<i class="fa-regular fa-file-lines"></i></a>')

        class Meta(BaseMeta):
            model = _model
            exclude = ('view',)

    return Table


class SetTable(table_factory(Set)):
    view = MetaColumn()
    assigned_to = tables.Column(accessor='distributor')
    date = tables.DateTimeColumn(accessor='date', format='Y-m-d')
    recipient = tables.Column(accessor='recipient')
    city = tables.Column(accessor='city')
    document = tables.Column(accessor='document')

    class Meta(BaseMeta):
        model = Set


class OrderTable(table_factory(Order)):
    view = MetaColumn()
    date = tables.DateTimeColumn(format='Y-m-d')
    sets = tables.ManyToManyColumn()

    class Meta(BaseMeta):
        model = Order
        exclude = ('id',)
