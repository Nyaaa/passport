"""Lookup channels for ajax-autocomplete"""
from ajax_select import register, LookupChannel
from .models import City, Item, Set


@register('city')
class CityLookup(LookupChannel):

    model = City

    def get_query(self, q, request):
        return self.model.objects.filter(name__icontains=q).order_by('name')


@register('article')
class ItemLookup(LookupChannel):

    model = Item
    min_length = 3

    def get_query(self, q, request):
        return self.model.objects.filter(article__icontains=q).order_by('article')[:10]


@register('set')
class SetLookup(LookupChannel):

    model = Set
    min_length = 3

    def get_query(self, q, request):
        return self.model.objects.filter(serial__icontains=q).order_by('serial')[:10]
