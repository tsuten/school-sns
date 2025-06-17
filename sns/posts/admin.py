from django.contrib import admin
from .models import Post, Like, Category, Tag

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'display_tags', 'is_public', 'created_at')
    list_filter = ('is_public', 'is_deleted', 'category', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    fieldsets = (
        (None, {'fields': ('user', 'title', 'content', 'category', 'tags')}),
        ('Status', {'fields': ('is_public', 'is_deleted', 'deleted_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Tags'

# Register your models here.
admin.site.register(Post, PostAdmin)
admin.site.register(Like)
admin.site.register(Category)
admin.site.register(Tag)