from django.contrib import admin

# Register your models here.
from .models import Tag,Warehouse,CustomUser,WarehouseImage,ProductList,Review,TopWarehouse,BillImage,AddWarehouse
admin.site.register(Tag)
admin.site.register(Warehouse)
admin.site.register(CustomUser)
admin.site.register(WarehouseImage)
admin.site.register(ProductList)
admin.site.register(Review)
admin.site.register(TopWarehouse)
admin.site.register(BillImage)
admin.site.register(AddWarehouse)