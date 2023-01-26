import django_filters
from .models import Item, Set, Series, Order


def filter_factory(_model):
    class NewFilter(django_filters.FilterSet):
        name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

        class Meta:
            model = _model
            fields = ['name']

    return NewFilter


class ItemFilter(django_filters.FilterSet):
    article = django_filters.CharFilter(field_name='article', lookup_expr='icontains')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    series = django_filters.ModelChoiceFilter(field_name='series', empty_label='All series', queryset=Series.objects.all())
    is_set = django_filters.ChoiceFilter(field_name='is_set', choices=(('1', 'Set'), ('0', 'Tool')), empty_label='All items')

    class Meta:
        model = Item
        fields = ['article', 'name', 'series', 'is_set']


class SetFilter(django_filters.FilterSet):
    article = django_filters.CharFilter(field_name='article', lookup_expr='icontains')
    serial = django_filters.CharFilter(field_name='serial', lookup_expr='icontains')

    class Meta:
        model = Set
        fields = ['article', 'serial']


class OrderFilter(django_filters.FilterSet):

    class Meta:
        model = Order
        fields = ['date', 'distributor', 'recipient', 'document', 'city']
