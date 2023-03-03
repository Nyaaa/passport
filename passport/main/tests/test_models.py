from django.test import TestCase
from main.models import Distributor, Recipient, ProtectedError, City, \
    Order, Series, Item, Set, item_img_path
from uuid import UUID
import re


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.d = Distributor.objects.get(pk=1)
        cls.r = Recipient.objects.get(pk=1)
        cls.c = City.objects.create(name='city')
        cls.s = Series.objects.create(name='series')
        cls.i = Item.objects.create(article='item_article', name='item_name')

    def test_series_str(self):
        self.assertEqual(str(self.s), 'series')

    def test_distributor_str(self):
        self.assertEqual(str(self.d), 'Warehouse')

    def test_distributor_delete(self):
        with self.assertRaises(ProtectedError):
            self.d.delete()

        obj = Distributor.objects.create(name='test')
        obj.delete()
        unprotected = Distributor.objects.filter(name='test')
        self.assertFalse(unprotected.exists())

    def test_recipient_str(self):
        self.assertEqual(str(self.r), '[Incomplete]')

    def test_recipient_delete(self):
        protected2 = Recipient.objects.get(pk=2)
        with self.assertRaises(ProtectedError):
            self.r.delete()
            protected2.delete()

        obj = Recipient.objects.create(name='test')
        obj.delete()
        unprotected = Recipient.objects.filter(name='test')
        self.assertFalse(unprotected.exists())

    def test_city_str(self):
        self.assertEqual(str(self.c), 'city')

    def test_order_str(self):
        obj = Order.objects.create(distributor=self.d, recipient=self.r, city=self.c)
        self.assertEqual(str(obj), '1')

    def test_order_url(self):
        obj = Order.objects.create(distributor=self.d, recipient=self.r, city=self.c)
        self.assertEqual(obj.get_absolute_url(), '/order/1/')

    def test_item_str(self):
        self.assertEqual(str(self.i), 'item_article')

    def test_item_url(self):
        self.assertEqual(self.i.get_absolute_url(), '/item/item_article/edit/')

    def test_set_str(self):
        obj = Set.objects.create(serial='0000', article=self.i)
        self.assertEqual(str(obj), '0000')

    def test_set_url(self):
        obj = Set.objects.create(serial='0000', article=self.i)
        self.assertEqual(obj.get_absolute_url(), '/set/0000/')

    def test_img_path(self):
        self.assertEqual(item_img_path(self.i, 'image.jpg'), 'item_img/item_article.jpg')
        gen_uuid = item_img_path(None, 'image.jpg')
        folder, uuid, ext = re.split(r'/|\.', gen_uuid)
        self.assertEqual(ext, 'jpg')
        self.assertEqual(folder, 'item_img')
        self.assertEqual(UUID(uuid).version, 4)
