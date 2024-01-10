from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from main.urls import urlpatterns


def get_url(page):
    """Create objects for reverse lookup to avoid error 404."""
    if ':pk>' in str(page.pattern):
        obj = baker.make(page.name.split('_')[0])
        return reverse(page.name, kwargs={'pk': obj.pk})
    return reverse(page.name)


class UrlTests(TestCase):
    def test_unauthorised_access(self):
        """No page should be available without logging in."""
        for page in urlpatterns:
            url = get_url(page)

            if page.name == 'login':
                continue
            expected_url = '/login/' if page.name == 'logout' else '/login/?next=' + url
            self.assertRedirects(self.client.get(url), expected_url, status_code=302, target_status_code=200,
                                 fetch_redirect_response=True)

    def test_authorised_access(self):
        """Check all pages for response code 200 for logged-in users."""
        user = get_user_model()
        user.objects.create_user(username='testuser', password='12345')
        self.assertTrue(self.client.login(username='testuser', password='12345'))

        for page in urlpatterns:
            if page.name == 'logout':
                continue
            url = get_url(page)
            self.assertEqual(self.client.get(url).status_code, 200)
