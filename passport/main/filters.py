import django_filters
from django import forms
from .models import Item


class ItemFilter(django_filters.FilterSet):
    article = django_filters.CharFilter(field_name='article', lookup_expr='icontains')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['article', 'name']
