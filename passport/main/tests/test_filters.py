from django.test import TestCase
from main.templatetags.custom_filters import get_values
from main.filters import SetFilter, filter_factory
from main.models import City, Item, Set
from main.lookups import CityLookup, ItemLookup, SetLookup


class TemplateTagsTests(TestCase):
    def test_get_values(self):
        dct = {'key': 'value'}
        self.assertEqual(get_values(dct, 'key'), 'value')


class FilterTests(TestCase):

    def test_set_filter(self):
        City.objects.create(name='Paris')
        City.objects.create(name='London')
        queryset = City.objects.all()
        result = City.objects.filter(name='London')
        self.assertQuerysetEqual(
            SetFilter.set_order_filter(queryset, 'name', 'London'), result)

    def test_filter_factory(self):
        self.assertTrue(filter_factory(City))
        self.assertTrue(filter_factory(City).Meta.model, City)


class LookupsTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.c = City.objects.create(name='Paris')
        cls.i = Item.objects.create(article='item_article', name='item_name')

    def test_city_lookup(self):
        queryset = City.objects.all()
        result = City.objects.filter(name='Paris')
        self.assertQuerysetEqual(
            CityLookup.get_query(queryset, 'Paris', ''), result)

    def test_item_lookup(self):
        queryset = Item.objects.all()
        result = Item.objects.filter(article='item_article')
        self.assertQuerysetEqual(
            ItemLookup.get_query(queryset, 'item_article', ''), result)

    def test_set_lookup(self):
        Set.objects.create(serial='0000', article=self.i)
        queryset = Set.objects.all()
        result = Set.objects.filter(serial='0000')
        self.assertQuerysetEqual(
            SetLookup.get_query(queryset, '0000', ''), result)

