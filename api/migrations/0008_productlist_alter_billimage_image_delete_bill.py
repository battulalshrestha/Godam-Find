# Generated by Django 5.1.1 on 2025-01-04 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_warehouse_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.CharField(choices=[('consumer_electronics', 'Consumer Electronics'), ('accessories', 'Accessories'), ('computer_hardware', 'Computer Hardware'), ('cameras_photography', 'Cameras and Photography Equipment'), ('networking_equipment', 'Networking Equipment'), ('power_tools', 'Power Tools and Other Electronics'), ('repair_parts', 'Repair Parts and Components')], max_length=70)),
            ],
        ),
        migrations.AlterField(
            model_name='billimage',
            name='image',
            field=models.ImageField(upload_to='media/bill_photo/'),
        ),
        migrations.DeleteModel(
            name='Bill',
        ),
    ]
