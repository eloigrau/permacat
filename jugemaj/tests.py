"""Django tests for the jugemaj app."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Candidate, Election


class JugeMajTests(TestCase):
    """Mais class for the tests."""
    def setUp(self):
        """Create a bunch of users for the other tests."""
        a, b, c = (User.objects.create_user(guy, email='%s@example.org' % guy, password=guy) for guy in 'abc')
        a.is_superuser = True
        a.save()

    def test_views(self):
        """Test the django views in the jugemaj app."""
        self.assertEqual(self.client.get(reverse('jugemaj:elections')).status_code, 200)
        self.assertEqual(self.client.get(reverse('jugemaj:create_election')).status_code, 302)
        self.client.login(username='a', password='a')
        self.assertEqual(self.client.get(reverse('jugemaj:create_election')).status_code, 200)
        r = self.client.post(
            reverse('jugemaj:create_election'), {
                'name': 'Élection du roi de Vénus',
                'description': 'Vénus n’a plus de roi, qui pensez-vous des candidats suivants ?',
                'end_0': '2025-03-09',
                'end_1': '03:19:45',
            })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Election.objects.count(), 1)
        slug = Election.objects.first().slug
        self.assertEqual(r.url, f'/election/{slug}')
        self.assertEqual(self.client.get(r.url).status_code, 200)
        self.assertEqual(self.client.get(reverse('jugemaj:election', kwargs={'slug': slug})).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(r.url).status_code, 200)
        self.assertEqual(self.client.get(reverse('jugemaj:create_candidate', kwargs={'slug': slug})).status_code, 302)
        self.client.login(username='b', password='b')
        self.assertEqual(self.client.get(reverse('jugemaj:create_candidate', kwargs={'slug': slug})).status_code, 200)
        r = self.client.post(reverse('jugemaj:create_candidate', kwargs={'slug': slug}), {'name': 'Capitaine Zorg'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, f'/election/{slug}')
        self.assertEqual(Candidate.objects.count(), 1)
        for name in ['Buzz l’Éclair', 'Timon et Pumba', 'Sénateur Palpatine', 'Aragorn', 'Totoro', 'Obi-Wan Kenobi']:
            r = self.client.post(reverse('jugemaj:create_candidate', kwargs={'slug': slug}), {'name': name})
        self.client.logout()
        url = reverse('jugemaj:vote', kwargs={'slug': slug})
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.login(username='b', password='b')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        data = {'csrf_token': r.context['csrf_token']}
        management_form = r.context['formset'].management_form
        for i in 'TOTAL_FORMS', 'INITIAL_FORMS', 'MIN_NUM_FORMS', 'MAX_NUM_FORMS':
            data['%s-%s' % (management_form.prefix, i)] = management_form[i].value()
        for i in range(r.context['formset'].total_form_count()):
            form = r.context['formset'].forms[i]
            for field in form.fields:
                data[f'{form.prefix}-{field}'] = i % 6 + 1

        self.assertEqual(self.client.post(url, data).status_code, 302)
        self.assertEqual(self.client.get(reverse('jugemaj:election', kwargs={'slug': slug})).status_code, 200)
