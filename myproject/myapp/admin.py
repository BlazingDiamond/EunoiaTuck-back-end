from django.contrib import admin
from myapp import models

admin.site.register(models.User)


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "account")
    search_fields = ("username", "email")
    list_filter = ("account",)


admin.site.register(models.Product)
admin.site.register(models.Account)
admin.site.register(models.Order)
admin.site.register(models.OrderItem)
