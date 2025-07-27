from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField
from django.db import models
from django.contrib.auth.models import User
import uuid
from tinymce.models import HTMLField
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from multiselectfield import MultiSelectField
import random
from django.urls import reverse
from django.contrib import admin
from django.core.validators import FileExtensionValidator






class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')

    def save(self, *args, **kwargs):
        # Validate fields before saving
        self.clean()
        super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s cart: {self.quantity} x {self.product.name}"

    def increase_quantity(self, count=1):
        self.quantity += count
        self.save()

    def decrease_quantity(self, count=1):
        if self.quantity > count:
            self.quantity -= count
            self.save()
        else:
            self.delete()




class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]



    name = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=20, editable=False, unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, default='M')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True) 


    def save(self, *args, **kwargs):
        if not self.customer_id:
            while True:
                random_number = f"{random.randint(100000, 999999)}"
                potential_id = f"#CUSTOMER#{random_number}"
                if not Profile.objects.filter(customer_id=potential_id).exists():
                    self.customer_id = potential_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user.username}"





class VideoProduct(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(
            allowed_extensions=['mp4', 'webm', 'ogg', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'mpeg', 'mpg']
        )]
    )
    product_image = models.FileField(upload_to='product_images/')
    actual_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        if self.actual_price > 0:
            return round(((self.actual_price - self.current_price) / self.actual_price) * 100)
        return 0




# Create your models here.
class Banner(models.Model):
     COLOR_CHOICES = [
          ('black','black'),
          ('white','white'),
     ]
     heading = models.CharField(max_length=250,blank=True, null=True)
     description = models.TextField(blank=True, null=True)
     button_text = models.CharField(max_length=100,blank=True, null=True)
     button_url = models.URLField(blank=True, null=True)
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
     image_for_desktop = models.FileField(upload_to='banners/desktop')
     image_for_mobile = models.FileField(upload_to='banners/desktop')
     status = models.BooleanField(default=True)
     color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='black')


     def __str__(self):
          return self.heading

class Gallery(models.Model):

     image = models.ImageField(upload_to='gallery/', null=True, blank=True)
     description = models.TextField(blank=True)  # Add this field
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return f"Gallery Image - {self.id}"


     class Meta:
        ordering = ['-created_at']
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'


class ScrollingImages(models.Model):

     image = models.ImageField(upload_to='scrolling-image/', null=True, blank=True)
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return f"Scrolling Image - {self.id}"


     class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scrolling-image'
        verbose_name_plural = 'Scrolling-images'

class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



CATEGORY_STATUS = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.FileField(upload_to='category_images/',null=True, blank=True)
    priority= models.IntegerField(default=100)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=CATEGORY_STATUS, default='active')
    slug = models.SlugField(unique=True, blank=True)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_products = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name



class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]

    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]

    PRODUCT_TYPE_CHOICES = [
        ('readymade', 'Readymade'),
        ('fabric', 'Fabric')
    ]


    STOCK_CHOICE = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out Of Stock')
    ]

    product_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to='category_images/',unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    in_stock = models.CharField(max_length=225, default='in_stock', choices=STOCK_CHOICE)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    tags = TaggableManager()
    description = HTMLField(blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    available_sizes = MultiSelectField(choices=SIZE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Generate the initial slug based on the product name
        if not self.pk and not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug

        # Call the original save method to save the model instance
        super().save(*args, **kwargs)



    def __str__(self):
        return self.name





class Accordion(models.Model):
    product = models.ForeignKey(Product, related_name='accordions', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = HTMLField(blank=True)

    def __str__(self):
        return f"{self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} Image"



class ProductVariant(models.Model):
    VARIANT_CHOICES = [
        ('color', 'Color'),
        ('size', 'Size'),
    ]

    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    variant_type = models.CharField(max_length=50, choices=VARIANT_CHOICES)
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product.name} - {self.variant_type}: {self.value}"


