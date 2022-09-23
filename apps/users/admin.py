# from django.contrib import admin

# # Register your models here.
# from .models import User

# admin.site.register(User)

from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
