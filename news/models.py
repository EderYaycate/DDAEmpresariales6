from django.db import models
from django.utils import timezone


class Author(models.Model):
    name = models.CharField('nombre', max_length=120)
    bio = models.TextField('biografía', blank=True)

    class Meta:
        verbose_name = 'autor'
        verbose_name_plural = 'autores'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('nombre', max_length=80, unique=True)
    slug = models.SlugField('slug', unique=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField('título', max_length=200)
    slug = models.SlugField('slug', unique=True)
    summary = models.TextField('resumen')
    body = models.TextField('cuerpo')
    featured_image = models.ImageField(
        'imagen destacada', upload_to='articles/', null=True, blank=True
    )
    published_at = models.DateTimeField('fecha de publicación', default=timezone.now)
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name='autor',
    )
    categories = models.ManyToManyField(
        Category, related_name='articles', verbose_name='categorías'
    )

    class Meta:
        verbose_name = 'noticia'
        verbose_name_plural = 'noticias'
        ordering = ['-published_at']

    def __str__(self):
        return self.title
