from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission,PermissionsMixin  #importing the AbstractBaseUser class
from django.db.models import Avg #importing the average function
from django.utils import timezone
# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50,unique=True)
    def __str__(self):
        return self.name
class Warehouse(models.Model):
    name =models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    opening_time = models.CharField(max_length=100)
    closing_time = models.CharField(max_length=100)
    description = models.TextField()
    map_url = models.CharField(max_length=1000,default='https://www.google.com/maps')
    tags = models.ManyToManyField(Tag,related_name='warehouses')
    
    def average_rating(self):
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        return round(avg_rating)
    def __str__(self):
        return self.name
    
    def no_of_reviews(self):
        return self.reviews.count()

class CustomUser(AbstractUser,PermissionsMixin):
    google_id = models.CharField(max_length=255,unique=True)
    email = models.EmailField(max_length=255,unique=True)
    profile_pic = models.URLField(null=True,default=None)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    user_fav_warehouses = models.ManyToManyField(Warehouse,related_name='fav_by')
    groups = models.ManyToManyField('auth.Group',related_query_name="custom_user",blank=True,verbose_name='groups')
    user_permissions = models.ManyToManyField('auth.Permission',related_name="custom_user_set"
    ,blank=True,verbose_name='user permissions')
    def __str__(self):
        return self.username
    
class WarehouseImage(models.Model):
    warehouse = models.ForeignKey(Warehouse,related_name='images',on_delete=models.CASCADE)
    image = models.ImageField(upload_to='warehouse_images/')
    

from django.db import models
from api.models import Warehouse
from api.models import WarehouseImage

class ProductList(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    category =models.CharField(max_length=70,choices= [
        ('consumer_electronics', 'Consumer Electronics'),
        ('accessories', 'Accessories'),
        ('computer_hardware', 'Computer Hardware'),
        ('cameras_photography', 'Cameras and Photography Equipment'),
        ('networking_equipment', 'Networking Equipment'),
        ('power_tools', 'Power Tools and Other Electronics'),
        ('repair_parts', 'Repair Parts and Components'),
    ])
    def __str__(self):
        return f"{self.name} - ${self.price}"
    def get_category_display(self):
        return dict(ProductList._meta.get_field('category').choices)[self.category]
    
class Review(models.Model):
    user = models.ForeignKey(CustomUser,related_name='reviews',on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse,related_name='reviews',on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_text = models.TextField(null=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Rating: {self.rating} for {self.warehouse.name}"
    
class TopWarehouse(models.Model):
    warehouse = models.OneToOneField('Warehouse',on_delete=models.CASCADE)
    ranking = models.IntegerField()
    
class BillImage(models.Model):
    image = models.ImageField(upload_to='media/bill_photo/')


class AddWarehouse(models.Model):
    user = models.ForeignKey(CustomUser,related_name ="add_user_request",on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    opening_time = models.CharField(max_length=100)
    closing_time = models.CharField(max_length=100)
    BillImages = models.ManyToManyField(BillImage,related_name='warehouse_images',blank=True)