# Generated by Django 4.2.20 on 2025-06-24 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_accordion_remove_product_small_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='accordion',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accordions', to='core.product'),
        ),
    ]
