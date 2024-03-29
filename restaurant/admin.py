from django.contrib import admin
from .models import Restaurant, Cuisine, Todo, Notification


# Register Restaurant model
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_verified']

# Register Cuisine model
@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'cuisine']

# Register Todo model
@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['done', 'note']

# Register Notification model
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'title', 'time']