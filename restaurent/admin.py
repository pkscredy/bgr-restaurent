from django.contrib import admin
from restaurent.models import ResData


@admin.register(ResData)
class RestaurentAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'url', 'location', 'review', 'rating')

    search_fields = ('name', 'rating',)
