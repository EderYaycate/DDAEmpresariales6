import io
import os
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw

from news.models import Article, Author, Category

CATEGORIES = [('Tecnología', 'tecnologia'), ('Deportes', 'deportes'), ('Cultura', 'cultura')]

AUTHORS = [
    ('Lucía Paredes', 'Periodista de tecnología con diez años de experiencia.'),
    ('Marco Salazar', 'Cronista deportivo y comentarista.'),
]

SUMMARY = (
    'Un resumen de prueba lo bastante largo para comprobar el recorte automático '
    'del texto en la portada: aquí se agregan palabras adicionales que no deberían '
    'verse completas en la tarjeta de la noticia.'
)

# (title, slug, categories, author index, days ago, color)
ARTICLES = [
    ('Nueva ola de inteligencia artificial en las aulas', 'ia-en-las-aulas', ['tecnologia'], 0, 1, (30, 90, 160)),
    ('Lanzan un satélite peruano de observación', 'satelite-peruano', ['tecnologia', 'cultura'], 0, 2, (20, 120, 120)),
    ('Final de liga: resumen y claves del partido', 'final-de-liga', ['deportes'], 1, 3, (160, 60, 40)),
    ('Atletas locales se preparan para los Juegos', 'atletas-locales', ['deportes'], 1, 4, (120, 60, 140)),
    ('Festival de cine reúne a nuevos directores', 'festival-de-cine', ['cultura'], 0, 5, (170, 120, 30)),
    ('Reabre el museo con una muestra inédita', 'reabre-el-museo', ['cultura'], 1, 6, (60, 110, 60)),
]


def make_image(title, color):
    """Build a simple gradient banner so the demo needs no external files."""
    width, height = 800, 450
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        shade = int(120 * y / height)
        line = tuple(max(c - shade // 2, 0) for c in color)
        draw.line([(0, y), (width, y)], fill=line)
    draw.text((30, height - 50), title[:60], fill=(255, 255, 255))
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = 'Load demo categories, authors, six articles and the demo superuser.'

    def handle(self, *args, **options):
        categories = {
            slug: Category.objects.get_or_create(slug=slug, defaults={'name': name})[0]
            for name, slug in CATEGORIES
        }
        authors = [
            Author.objects.get_or_create(name=name, defaults={'bio': bio})[0]
            for name, bio in AUTHORS
        ]

        now = timezone.now()
        for title, slug, cat_slugs, author_idx, days_ago, color in ARTICLES:
            article, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'summary': SUMMARY,
                    'body': f'{title}.\n\nPrimer párrafo del cuerpo de la noticia.\n\n'
                            'Segundo párrafo con más detalles.',
                    'author': authors[author_idx],
                    'published_at': now - timedelta(days=days_ago),
                },
            )
            article.categories.set([categories[s] for s in cat_slugs])
            if created or not article.featured_image:
                article.featured_image.save(f'{slug}.jpg', make_image(title, color), save=True)

        password = os.environ.get('DEMO_ADMIN_PASSWORD', 'Admin12345!')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', password)

        self.stdout.write(self.style.SUCCESS(
            f'Demo ready: {Article.objects.count()} articles, '
            f'{Category.objects.count()} categories, {Author.objects.count()} authors.'
        ))
