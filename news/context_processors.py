from django.db.models import Count

from .models import Category


def categories(request):
    """Expose the categories (with article counts) to every template."""
    return {
        'sidebar_categories': Category.objects.annotate(total=Count('articles')),
    }
