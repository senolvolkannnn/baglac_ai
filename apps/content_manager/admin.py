from django.contrib import admin
from .models import Content, Category, ContentVersion

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('type',)
    search_fields = ('name', 'description')

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):
    list_display = ('content', 'version_number', 'created_at', 'created_by')
    list_filter = ('created_by', 'created_at') 