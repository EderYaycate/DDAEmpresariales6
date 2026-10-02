import shutil
import tempfile

from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Article, Author, Category

TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_demo', verbosity=0)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def test_demo_loads_six_articles_in_three_categories(self):
        self.assertEqual(Article.objects.count(), 6)
        self.assertEqual(Category.objects.count(), 3)

    def test_home_lists_all_articles(self):
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['articles']), 6)
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'news/_article_card.html')

    def test_summary_is_truncated_on_the_card(self):
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, '…')
        self.assertNotContains(response, 'de la noticia.')

    def test_card_fragment_is_reused_in_category_page(self):
        category = Category.objects.get(slug='deportes')
        response = self.client.get(reverse('news:category_detail', args=[category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/_article_card.html')
        self.assertEqual(len(response.context['articles']), 2)

    def test_detail_shows_author_and_categories(self):
        article = Article.objects.get(slug='satelite-peruano')
        response = self.client.get(reverse('news:article_detail', args=[article.slug]))
        self.assertContains(response, article.author.name)
        self.assertContains(response, 'Tecnología')
        self.assertContains(response, 'Cultura')

    def test_unknown_slug_returns_404(self):
        response = self.client.get(reverse('news:article_detail', args=['no-existe']))
        self.assertEqual(response.status_code, 404)

    def test_sidebar_is_present_on_every_page(self):
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, 'Categorías')

    def test_stylesheet_is_found_and_linked(self):
        self.assertIsNotNone(finders.find('css/styles.css'))
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, '/static/css/styles.css')

    def test_featured_images_are_stored(self):
        for article in Article.objects.all():
            self.assertTrue(article.featured_image.storage.exists(article.featured_image.name))

    def test_html_in_body_is_escaped(self):
        article = Article.objects.create(
            title='Prueba de escapado',
            slug='prueba-escapado',
            summary='Resumen',
            body='<script>alert("x")</script> y <b>negrita</b>',
            author=Author.objects.first(),
            published_at=timezone.now(),
        )
        response = self.client.get(reverse('news:article_detail', args=[article.slug]))
        self.assertContains(response, '&lt;script&gt;')
        self.assertContains(response, '&lt;b&gt;negrita&lt;/b&gt;')
        self.assertNotContains(response, '<script>alert')


class EmptyPortalTests(TestCase):
    def test_empty_message_when_no_articles(self):
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, 'Aún no hay noticias publicadas.')

    def test_empty_message_in_category_without_articles(self):
        category = Category.objects.create(name='Vacía', slug='vacia')
        response = self.client.get(reverse('news:category_detail', args=[category.slug]))
        self.assertContains(response, 'No hay noticias en esta categoría.')
