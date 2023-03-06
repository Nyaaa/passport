from django.test import TestCase
from main.forms import SetForm, modelform_init
from main.models import Item, City,Set
from model_bakery import baker


class FormTests(TestCase):
    def test_set_form_invalid_serial(self):
        item = Item.objects.create(article='item_article', name='item_name')
        data = [{'serial': 'AB123C-000a', 'article': item},
                {'serial': 'AB123C-aaaa', 'article': item},
                {'serial': 'AB123C-', 'article': item},
                {'serial': 'AB123C', 'article': item}]
        for i in data:
            form = SetForm(data=i)
            self.assertFalse(form.is_valid())

    def test_set_form_clean_valid(self):
        item = Item.objects.create(article='item_article', name='item_name')
        form = SetForm(data={'serial': ' ab123c-0001 ', 'article': item})
        self.assertTrue(form.is_valid())
        saved = form.save()
        self.assertEqual(saved.serial, 'AB123C-0001')

    def test_set_form_exists(self):
        item = Item.objects.create(article='item_article', name='item_name')
        baker.make(Set, serial='AB123C-0001')
        set2 = baker.make(Set, serial='AB123C-0002')
        form = SetForm(instance=set2, data={'serial': 'AB123C-0001', 'article': item})
        self.assertFalse(form.is_valid())

    def test_modelform(self):
        self.assertTrue(modelform_init(Item))
        self.assertTrue(modelform_init(Item).Meta.model, Item)

    def test_modelform_clean_name(self):
        form_class = modelform_init(City)
        form = form_class(data={'name': '  London   '})
        self.assertTrue(form.is_valid())
        saved = form.save()
        self.assertEqual(saved.name, 'London')

    def test_modelform_clean_article(self):
        form_class = modelform_init(Item)
        form = form_class(data={'article': 'ab123c ', 'name': 'item_name'})
        self.assertTrue(form.is_valid())
        saved = form.save()
        self.assertEqual(saved.article, 'AB123C')
