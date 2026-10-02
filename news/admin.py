from django.contrib import admin

from .models import Article, Author, Category


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category_list', 'published_at')
    list_filter = ('categories', 'author', 'published_at')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories',)
    date_hierarchy = 'published_at'
    list_select_related = ('author',)

    @admin.display(description='categorías')
    def category_list(self, obj):
        return ', '.join(c.name for c in obj.categories.all())

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')
