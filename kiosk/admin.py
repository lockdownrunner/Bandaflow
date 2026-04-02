from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Supplier, Transaction

admin.site.register(User, UserAdmin)
admin.site.register(Supplier)
admin.site.register(Transaction)
