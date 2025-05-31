from django.db import models

# Create your models here.
class Address(models.Model):
  name = models.CharField(max_length=255)
  email = models.EmailField(unique=True)
  phone = models.IntegerField()
  message = models.CharField(max_length=1000)
  def __str__(self):
    return f'{self.name}-{self.phone}'
  
class MomoItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/')
    category = models.CharField(max_length=100, choices=[
        ('Buff', 'Buff'),
        ('Chicken', 'Chicken'),
        ('Veg', 'Veg'),
        ('Mutton', 'Mutton'),
    ])
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)


    def __str__(self):
        return self.name

