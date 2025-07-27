from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser

# Register your models here.
admin.site.register(Banner)
admin.site.register(Gallery)
admin.site.register(ScrollingImages)
admin.site.register(Message)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(VideoProduct)
admin.site.register(Profile)
admin.site.register(Cart)
