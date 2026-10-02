from django.shortcuts import get_object_or_404, render

from .models import Article, Category


def _articles():
    return Article.objects.select_related('author').prefetch_related('categories')


def home(request):
    return render(request, 'news/home.html', {'articles': _articles()})


def article_detail(request, slug):
    article = get_object_or_404(_articles(), slug=slug)
    return render(request, 'news/article_detail.html', {'article': article})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = _articles().filter(categories=category)
    return render(
        request,
        'news/category_detail.html',
        {'category': category, 'articles': articles},
    )
