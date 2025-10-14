from django.contrib import admin
from .models import Worker

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'last_name', 'first_name', 'middle_name', 'position', 'is_active', 'email', 'hired_date', 'created_by',
    )
    list_display_links = ('id', 'last_name')

    list_editable = ('is_active', 'position',)

    list_filter = ('is_active', 'position', 'created_by', 'hired_date')

    search_fields = ('last_name', 'first_name', 'middle_name', 'email', 'position')

    date_hierarchy = 'hired_date'
