import django_filters
from .models import Item, Set, Series


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

    class Meta:
        model = Item
        fields = ['article', 'name']


class SetFilter(django_filters.FilterSet):
    set_article = django_filters.CharFilter(field_name='set_article', lookup_expr='icontains')
    serial = django_filters.CharFilter(field_name='serial', lookup_expr='icontains')
    series = django_filters.ModelChoiceFilter(field_name='series', empty_label='All series', lookup_expr='exact',
                                              queryset=Series.objects.all())

    class Meta:
        model = Set
        fields = ['set_article', 'serial', 'series']
