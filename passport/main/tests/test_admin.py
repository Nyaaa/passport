from django.contrib.auth import get_user_model
from django.test import TestCase
from model_bakery import baker

from main.models import Order, Set


class AdminTests(TestCase):
    def setUp(self) -> None:
        user = get_user_model()
        self.admin = user.objects.create_superuser(username='admin', password='password')
        self.client.login(username='admin', password='password')

        set1 = baker.make(Set, make_m2m=True)
        baker.make(Order, sets=[set1])

    def test_set_admin(self):
        response = self.client.get('/admin/main/set/')
        self.assertEqual(response.status_code, 200)


