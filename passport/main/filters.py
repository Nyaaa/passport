from django_filters import FilterSet, CharFilter, ModelChoiceFilter, ChoiceFilter, DateFilter, NumberFilter
from .models import Item, Set, Series, Order, Distributor, Recipient, City
from django import forms
from ajax_select.fields import AutoCompleteWidget


def filter_factory(_model):
    """
    Create universal filter for basic models
    Args:
        _model (): Django model with 'name' field

    Returns:
        filter(FilterSet)
    """
    class NewFilter(FilterSet):
        name = CharFilter(lookup_expr='icontains')

        class Meta:
            model = _model
            fields = ['name']

    return NewFilter


class ItemFilter(FilterSet):
    article = CharFilter(lookup_expr='icontains')
    name = CharFilter(lookup_expr='icontains')
    series = ModelChoiceFilter(empty_label='All series', queryset=Series.objects.all())
    is_set = ChoiceFilter(empty_label='All items', choices=(('1', 'Set'), ('0', 'Tool')))

    class Meta:
        model = Item
        fields = ['article', 'name', 'series', 'is_set']


class SetFilter(FilterSet):
    article = CharFilter(field_name='article__article', lookup_expr='icontains', label='Article contains')
    serial = CharFilter(lookup_expr='icontains')
    comment = CharFilter(lookup_expr='icontains')
    distributor = ModelChoiceFilter(empty_label='All distributors', queryset=Distributor.objects.all().order_by('name'),
                                    method='set_order_filter', label='Distributor')
    recipient = ModelChoiceFilter(empty_label='All recipients', queryset=Recipient.objects.all().order_by('name'),
                                  method='set_order_filter', label='Recipient')
    city = ModelChoiceFilter(empty_label='All cities', queryset=City.objects.all().order_by('name'),
                             method='set_order_filter', label='City')
    document = NumberFilter(label='Document', method='set_order_filter')

    @staticmethod
    def set_order_filter(queryset, name, value):
        return queryset.filter(**{name: value})

    class Meta:
        model = Set
        fields = ['article', 'serial', 'comment']


class OrderFilter(FilterSet):
    date_from = DateFilter(field_name='date', lookup_expr='gt', widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = DateFilter(field_name='date', lookup_expr='lt', widget=forms.DateInput(attrs={'type': 'date'}))
    sets = ModelChoiceFilter(queryset=Set.objects.all(), widget=AutoCompleteWidget('set'))
    distributor = ModelChoiceFilter(empty_label='All distributors', queryset=Distributor.objects.all().order_by('name'))
    recipient = ModelChoiceFilter(empty_label='All recipients', queryset=Recipient.objects.all().order_by('name'))
    city = ModelChoiceFilter(empty_label='All cities', queryset=City.objects.all().order_by('name'))

    class Meta:
        model = Order
        fields = ['date_from', 'date_to', 'distributor', 'recipient', 'city', 'document']
