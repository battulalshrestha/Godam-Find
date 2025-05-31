from django.contrib import admin

# Register your models here.
from .models import Address
from .models import MomoItem
from unfold import admin as unfold_admin 
class AdressAdmin(unfold_admin.ModelAdmin):
    pass
admin.site.register(Address)
admin.site.register(MomoItem)
