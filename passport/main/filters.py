import django_filters
from .models import Item, Set, Series, Order, Distributor, Recipient, City
from django import forms


def filter_factory(_model):
    class NewFilter(django_filters.FilterSet):
        name = django_filters.CharFilter(lookup_expr='icontains')

        class Meta:
            model = _model
            fields = ['name']

    return NewFilter


class ItemFilter(django_filters.FilterSet):
    article = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(lookup_expr='icontains')
    series = django_filters.ModelChoiceFilter(empty_label='All series', queryset=Series.objects.all())
    is_set = django_filters.ChoiceFilter(empty_label='All items', choices=(('1', 'Set'), ('0', 'Tool')))

    class Meta:
        model = Item
        fields = ['article', 'name', 'series', 'is_set']


class SetFilter(django_filters.FilterSet):
    article = django_filters.CharFilter(lookup_expr='icontains')
    serial = django_filters.CharFilter(lookup_expr='icontains')
    comment = django_filters.CharFilter(lookup_expr='icontains')
    distributor = django_filters.ModelChoiceFilter(empty_label='All distributors', queryset=Distributor.objects.all(),
                                                   method='set_order_filter')
    recipient = django_filters.ModelChoiceFilter(empty_label='All recipients', queryset=Recipient.objects.all(),
                                                 method='set_order_filter')
    city = django_filters.ModelChoiceFilter(empty_label='All cities', queryset=City.objects.all(),
                                            method='set_order_filter')
    document = django_filters.CharFilter(label='Document №', method='set_order_filter')

    @staticmethod
    def set_order_filter(queryset, name, value):
        return queryset.filter(pk__in=Order.objects.filter(**{name: value}).values_list('sets'))

    class Meta:
        model = Set
        fields = ['article', 'serial', 'comment']


class OrderFilter(django_filters.FilterSet):
    # TODO: date range picker
    date = django_filters.DateFilter(lookup_expr='gt', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Order
        fields = ['date', 'distributor', 'recipient', 'document', 'city']
