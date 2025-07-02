from django.test import TestCase, Client
from django.urls import reverse
from ad.models import User
from .models import Ad, Category, ExchangeProposal

class AdViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        self.category = Category.objects.create(name='Игрушки')

        self.ad1 = Ad.objects.create(
            title='Плюшевый мишка',
            description='Мягкий мишка в хорошем состоянии',
            article='abc123',
            condition='used',
            user=self.user1,
            category=self.category
        )
        self.ad2 = Ad.objects.create(
            title='Конструктор LEGO',
            description='Почти новый',
            article='lego001',
            condition='new',
            user=self.user2,
            category=self.category
        )

    def test_ad_detail_view(self):
        response = self.client.get(reverse('ad:ad_detail', args=[self.ad1.article]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad1.title)

    def test_ad_create_view(self):
        self.client.login(username='user1', password='12345')
        response = self.client.post(reverse('ad:ad_create'), {
            'title': 'Самокат',
            'description': 'Хороший',
            'article': 'scooter123',
            'condition': 'used',
            'category': self.category.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='Самокат').exists())

    def test_ad_edit_view(self):
        self.client.login(username='user1', password='12345')
        response = self.client.post(reverse('ad:ad_edit', args=[self.ad1.article]), {
            'title': 'Обновленное название',
            'description': self.ad1.description,
            'article': self.ad1.article,
            'condition': self.ad1.condition,
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302)
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.title, 'Обновленное название')

