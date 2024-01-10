from django.test import TestCase
from django.test.client import RequestFactory

from main.models import City
from main.tables import table_factory


class TableTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        request = RequestFactory()
        get_request = request.get('/city/?name=London')
        table_class = table_factory(City)
        cls.table = table_class(data='', request=get_request)
        cls.get_request = get_request
        cls.c = City.objects.create(name='London')

    def test_table_factory_init(self):
        self.assertEqual(self.table.Meta.model, City)
        self.assertEqual(self.table.request, self.get_request)
        self.assertEqual(self.table.q_str, 'name=London')

    def test_table_factory_render_edit(self):
        expected = 'href="1/edit/?name=London"'
        self.assertIn(expected, self.table.render_edit(self.c))

    def test_table_factory_render_view(self):
        expected = 'href="1/?name=London"'
        self.assertIn(expected, self.table.render_view(self.c))
