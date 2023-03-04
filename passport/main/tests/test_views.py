from django.test import TestCase, RequestFactory
from model_bakery import baker
from main.views import CommonUpdateView, CommonDeleteView, CommonListView, ItemListView, SetListView, SetUpdateView
from main.models import Recipient, Item, Set, Order
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.handlers.wsgi import WSGIRequest


class ViewTests(TestCase):
    def prepare_post_request(self, request: WSGIRequest) -> WSGIRequest:
        request.user = self.user
        request.session = 'session'
        request._messages = FallbackStorage(request)
        return request

    def setUp(self) -> None:
        user = get_user_model()
        self.user = user.objects.create_user(username='user1', password='12345')
        self.client.login(username='user1', password='12345')

    def test_common_update(self):
        obj = Recipient.objects.get(pk=1)
        request = RequestFactory().get(reverse('recipient_edit', kwargs={'pk': obj.pk}))
        view = CommonUpdateView(model=Recipient, object=obj)
        view.setup(request=request)
        self.assertEqual(view.model, Recipient)
        self.assertTrue(view.get_success_message(view))
        self.assertEqual(self.client.get(view.get_success_url()).status_code, 200)
        context = view.get_context_data()
        func, *_ = resolve(reverse('recipient_delete', kwargs={'pk': obj.pk}))
        self.assertTrue(context['title'])
        self.assertEqual(func.view_class, CommonDeleteView)

    def test_common_list_get(self):
        request = RequestFactory().get(reverse('recipient'))
        view = CommonListView(model=Recipient)
        view.setup(request=request)
        self.assertEqual(view.model, Recipient)
        self.assertTrue(view.get_success_message(view))
        context = view.get_context_data()
        self.assertTrue(context['title'])

    def test_common_list_post(self):
        request = RequestFactory().post(reverse('recipient'), data={'name': 'test'})
        request = self.prepare_post_request(request)
        response = CommonListView.as_view(model=Recipient)(request)
        self.assertEqual(response.status_code, 302)

    def test_common_delete_get(self):
        obj = baker.make(Recipient)
        request = RequestFactory().get(reverse('recipient_delete', kwargs={'pk': obj.pk}))
        view = CommonDeleteView(model=Recipient)
        view.setup(request=request)
        self.assertEqual(view.model, Recipient)
        self.assertEqual(self.client.get(view.get_success_url()).status_code, 200)

    def test_common_delete_post_regular(self):
        obj = baker.make(Recipient)
        request = RequestFactory().post(reverse('recipient_delete', kwargs={'pk': obj.pk}))
        request = self.prepare_post_request(request)
        response = CommonDeleteView.as_view(model=Recipient)(request, **{'pk': obj.pk})
        self.assertEqual(response.status_code, 302)

    def test_common_delete_post_protected(self):
        obj = Recipient.objects.get(pk=1)
        request = RequestFactory().post(reverse('recipient_delete', kwargs={'pk': obj.pk}))
        request = self.prepare_post_request(request)
        CommonDeleteView.as_view(model=Recipient)(request, **{'pk': obj.pk})
        self.assertTrue(Recipient.objects.get(pk=1))

    def test_item_list(self):
        request = RequestFactory().post(reverse('item'), data={'article': 'aaa', 'name': 'test'})
        request = self.prepare_post_request(request)
        response = ItemListView.as_view(model=Item)(request)
        self.assertEqual(response.status_code, 302)

    def test_set_list_post_normal(self):
        item = baker.make(Item, is_set=True)
        request = RequestFactory().post(reverse('set'), data={'article': item})
        request = self.prepare_post_request(request)
        SetListView.as_view(model=Set)(request)
        self.assertTrue(Set.objects.get(article=item.article))

    def test_set_list_post_second_set(self):
        item = baker.make(Item, article='AA111B', is_set=True)
        baker.make(Set, article=item, serial='AA111B-0001')
        request = RequestFactory().post(reverse('set'), data={'article': item})
        request = self.prepare_post_request(request)
        SetListView.as_view(model=Set)(request)
        set2 = Set.objects.all().last()
        self.assertEqual(set2.serial, 'AA111B-0002')

    def test_set_list_post_used(self):
        item = baker.make(Item, article='USED-AA111B', is_set=True)
        request = RequestFactory().post(reverse('set'), data={'article': item})
        request = self.prepare_post_request(request)
        SetListView.as_view(model=Set)(request)
        set2 = Set.objects.all().last()
        self.assertEqual(set2.serial, 'AA111B-0001')

    def test_set_list_post_m2m(self):
        item = baker.make(Item, article='AA111B', is_set=True)
        set_items = baker.make(Item, _quantity=5)
        set1 = baker.make(Set, article=item, serial='AA111B-0001', items=set_items)
        request = RequestFactory().post(reverse('set'), data={'article': item})
        request = self.prepare_post_request(request)
        SetListView.as_view(model=Set)(request)
        set2 = Set.objects.all().last()
        self.assertQuerysetEqual(set1.items.all().order_by('pk'), set2.items.all().order_by('pk'))

    def test_set_detail(self):
        set1 = baker.make(Set, serial='111', make_m2m=True)
        response = self.client.get(reverse('set_detail', kwargs={'pk': set1.pk}))
        self.assertTrue(response.context['set_items']['111'])

    def test_set_update_set(self):
        item = baker.make(Item, is_set=True)
        set1 = baker.make(Set, article=item, serial='AAA-111', make_m2m=True)
        request = RequestFactory().post(reverse('set_edit', kwargs={'pk': set1}),
                                        data={'article': item, 'serial': 'aaa-222'})
        request = self.prepare_post_request(request)
        SetUpdateView.as_view()(request, pk=set1.pk)
        self.assertTrue(Set.objects.get(serial='AAA-222'))

    def test_order_list(self):
        response = self.client.post(reverse('order'), data={'set': ''})
        self.assertRedirects(response, reverse('order_create'), status_code=302, target_status_code=200,
                             fetch_redirect_response=True)

    def test_order_create(self):
        order = baker.make(Order, make_m2m=True)
        response = self.client.post(reverse('order_create'), data={'distributor': order.distributor.pk,
                                                                   'recipient': order.recipient.pk,
                                                                   'city': order.city.pk,
                                                                   'sets': order.sets.all()
                                                                   })

        self.assertRedirects(response, reverse('order_detail', kwargs={'pk': 2}),
                             status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_order_update(self):
        order = baker.make(Order, make_m2m=True)
        response = self.client.post(reverse('order_edit', kwargs={'pk': 1}),
                                    data={'distributor': order.distributor.pk,
                                          'recipient': order.recipient.pk,
                                          'city': order.city.pk,
                                          'sets': order.sets.all()
                                          })

        self.assertRedirects(response, reverse('order'),
                             status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_order_detail(self):
        set1 = baker.make(Set, make_m2m=True)
        order = baker.make(Order, sets=[set1])
        response = self.client.get(reverse('order_detail', kwargs={'pk': order.pk}))
        self.assertTrue(response.context['set_items'])
