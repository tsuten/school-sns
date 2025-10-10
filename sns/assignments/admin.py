from django.contrib import admin
from .models import Assignment

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'due_date', 'is_deleted', 'created_at')
    list_filter = ('is_deleted', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    filter_horizontal = ('assigned_to',)
    date_hierarchy = 'due_date'
    
    fieldsets = (
        (None, {'fields': ('title', 'description', 'created_by', 'assigned_to')}),
        ('Timeline', {'fields': ('due_date',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'deleted_at')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by').prefetch_related('assigned_to')

# Register your models here.
admin.site.register(Assignment, AssignmentAdmin)
