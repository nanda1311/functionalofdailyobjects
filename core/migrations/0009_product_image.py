# Generated by Django 4.2.20 on 2025-06-03 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_product_remove_message_slug_alter_category_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, unique=True, upload_to='category_images/'),
        ),
    ]
