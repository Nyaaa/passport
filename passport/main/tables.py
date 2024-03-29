import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Order, Set


class MetaColumn(tables.Column):
    def __init__(self, *args, **kwargs) -> None:
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

        def __init__(self, *args, **kwargs) -> None:
            """
            Get request from CommonListView to make urls with query string
            Args:
                **kwargs (): request
            """
            self.request = kwargs.pop('request')
            super().__init__(*args, **kwargs)
            self.q_str = self.request.GET.urlencode()

        def render_edit(self, record):
            return format_html(f'<a href="{record.pk}/edit/?{self.q_str}">'
                               '<i class="bi bi-pencil-square"></i></a>')

        def render_view(self, record):
            return format_html(f'<a href="{record.pk}/?{self.q_str}">'
                               '<i class="bi bi-file-earmark-text"></i></a>')

        class Meta(BaseMeta):
            model = _model
            exclude = ('view',)

    return Table


class SetTable(table_factory(Set)):
    view = MetaColumn()
    date = tables.DateTimeColumn(accessor='date', short=True, verbose_name=_('Date'))
    distributor = tables.Column(accessor='distributor', verbose_name=_('Distributor'))
    recipient = tables.Column(accessor='recipient', verbose_name=_('Recipient'))
    city = tables.Column(accessor='city', verbose_name=_('City'))
    document = tables.Column(accessor='document', verbose_name=_('Document'))

    class Meta(BaseMeta):
        model = Set


class OrderTable(table_factory(Order)):
    view = MetaColumn()
    date = tables.DateTimeColumn(short=True)
    sets = tables.ManyToManyColumn()

    class Meta(BaseMeta):
        model = Order
        exclude = ('id',)
