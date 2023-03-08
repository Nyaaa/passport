from django.test import TestCase, RequestFactory
from model_bakery import baker
from main.views import CommonUpdateView, CommonDeleteView, CommonListView
from main.models import Recipient, Item, Set, Order
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model


class ViewTests(TestCase):
    def setUp(self) -> None:
        self.client.login(username='user1', password='12345')

    @classmethod
    def setUpTestData(cls) -> None:
        user = get_user_model()
        user.objects.create_user(username='user1', password='12345')
        cls.item_is_set = baker.make(Item, article='AA111B', is_set=True)
        cls.recipient_protected = Recipient.objects.get(pk=1)
        set1 = baker.make(Set, make_m2m=True)
        cls.order = baker.make(Order, sets=[set1])

    def test_common_update(self):
        request = RequestFactory().get(reverse('recipient_edit', kwargs={'pk': self.recipient_protected.pk}))
        view = CommonUpdateView(model=Recipient, object=self.recipient_protected)
        view.setup(request=request)
        self.assertEqual(view.model, Recipient)
        self.assertTrue(view.get_success_message(view))
        self.assertEqual(self.client.get(view.get_success_url()).status_code, 200)
        context = view.get_context_data()
        func, *_ = resolve(reverse('recipient_delete', kwargs={'pk': self.recipient_protected.pk}))
        self.assertTrue(context['title'])
        self.assertEqual(func.view_class, CommonDeleteView)

    def test_common_update_post(self):
        obj = baker.make(Recipient, name='test111')
        self.client.post(reverse('recipient_edit', kwargs={'pk': obj.pk}), data={'name': 'test222'})
        obj.refresh_from_db()
        self.assertEqual(obj.name, 'test222')

    def test_common_list_get(self):
        request = RequestFactory().get(reverse('recipient'))
        view = CommonListView(model=Recipient)
        view.setup(request=request)
        self.assertEqual(view.model, Recipient)
        self.assertTrue(view.get_success_message(view))
        context = view.get_context_data()
        self.assertTrue(context['title'])

    def test_common_list_post(self):
        response = self.client.post(reverse('recipient'), data={'name': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Recipient.objects.filter(name='test').exists())

    def test_common_delete_get(self):
        request = RequestFactory().get(reverse('recipient_delete', kwargs={'pk': self.recipient_protected.pk}))
        view = CommonDeleteView(model=Recipient)
        view.setup(request=request)
        self.assertEqual(view.model, Recipient)
        self.assertEqual(self.client.get(view.get_success_url()).status_code, 200)

    def test_common_delete_post_regular(self):
        obj = baker.make(Recipient)
        response = self.client.post(reverse('recipient_delete', kwargs={'pk': obj.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Recipient.objects.filter(pk=obj.pk).exists())

    def test_common_delete_post_protected(self):
        self.client.post(reverse('recipient_delete', kwargs={'pk': self.recipient_protected.pk}))
        self.assertTrue(Recipient.objects.filter(pk=1).exists())

    def test_item_list_post(self):
        self.client.post(reverse('item'), data={'article': 'aaa', 'name': 'test'})
        self.assertTrue(Item.objects.filter(article='AAA').exists())

    def test_set_list_post_normal(self):
        self.client.post(reverse('set'), data={'article': self.item_is_set})
        self.assertTrue(Set.objects.filter(article=self.item_is_set.article).exists())

    def test_set_list_post_second_set(self):
        baker.make(Set, article=self.item_is_set, serial='AA111B-0001')
        self.client.post(reverse('set'), data={'article': self.item_is_set})
        self.assertTrue(Set.objects.filter(serial='AA111B-0002').exists())

    def test_set_list_post_used(self):
        item = baker.make(Item, article='USED-AA111B', is_set=True)
        self.client.post(reverse('set'), data={'article': item})
        self.assertTrue(Set.objects.filter(serial='AA111B-0001').exists())

    def test_set_list_post_m2m(self):
        set1 = baker.make(Set, article=self.item_is_set, serial='AA111B-0001', make_m2m=True)
        self.client.post(reverse('set'), data={'article': self.item_is_set})
        set2 = Set.objects.get(serial='AA111B-0002')
        self.assertQuerysetEqual(set1.items.all().order_by('pk'), set2.items.all().order_by('pk'))

    def test_set_detail(self):
        set1 = baker.make(Set, serial='111', make_m2m=True)
        response = self.client.get(reverse('set_detail', kwargs={'pk': set1.pk}))
        self.assertTrue(response.context['set_items']['111'])

    def test_set_update_form_valid(self):
        set1 = baker.make(Set, article=self.item_is_set, serial='AA111B-111', make_m2m=True)
        self.client.post(reverse('set_edit', kwargs={'pk': set1}),
                         data={'article': self.item_is_set, 'serial': 'aa111b-222'})
        self.assertTrue(Set.objects.get(serial='AA111B-222'))

    def test_set_update_form_invalid(self):
        set1 = baker.make(Set, article=self.item_is_set, serial='AA111B-111', make_m2m=True)
        response = self.client.post(reverse('set_edit', kwargs={'pk': set1}),
                                    data={'article': self.item_is_set, 'serial': 'AA111B-111a'}, follow=True)
        self.assertFormError(response, 'form', 'serial', 'Serial number must follow the pattern [article]-[digits].')

    def test_order_list(self):
        response = self.client.post(reverse('order'), data={'set': ''})
        self.assertRedirects(response, reverse('order_create'), status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

    def test_order_create(self):
        response = self.client.post(reverse('order_create'), data={'distributor': self.order.distributor.pk,
                                                                   'recipient': self.order.recipient.pk,
                                                                   'city': self.order.city.pk,
                                                                   'sets': self.order.sets.all()
                                                                   })

        self.assertRedirects(response, reverse('order_detail', kwargs={'pk': 2}),
                             status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_order_update(self):
        response = self.client.post(reverse('order_edit', kwargs={'pk': 1}),
                                    data={'distributor': self.order.distributor.pk,
                                          'recipient': self.order.recipient.pk,
                                          'city': self.order.city.pk,
                                          'sets': self.order.sets.all()
                                          })

        self.assertRedirects(response, reverse('order'),
                             status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_order_detail(self):
        response = self.client.get(reverse('order_detail', kwargs={'pk': self.order.pk}))
        self.assertTrue(response.context['set_items'])
