from django.contrib import admin
from django.urls import path,include
from . import views
from django.shortcuts import render
from .models import Product
from django.conf import settings
from django.conf.urls.static import static


from .views import customer_list, customer_detail



urlpatterns = [
     # signin and signup for frontent
     path('account/signin/', views.admin_login, name='login'),

     path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
     path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),





     path('signup/', views.signup_view, name='signup'),
     path('signin/', views.signin_view, name='signin'),
     path('signout/', views.signout, name='signout'),



     path('', views.home, name="home"),
     path('account/artists/', views.artist_page, name="artist_page"),
     path('shop/', views.shop, name='shop'),
     path('product/<slug:slug>/', views.product_detail, name='product_detail'),
     path('cart/', views.cart, name='cart'),
     path('product/category/<slug:slug>/', views.cateogry_products, name='cateogry_products'),


     #login is for dashboard
     path('account/logout/', views.logout_user, name="logout"),

     # backend
     path('account/', views.dashboard, name="dashboard"),



     # category
     path('account/categories/', views.categories, name="categories"),
     path('category/<slug:slug>/edit/', views.categories, name='edit_category'),
     path('category/<slug:slug>/delete/', views.categories, name='delete_category'),


     # product
     path('account/products/', views.products, name='products'),
     path('account/create/product/', views.create_product, name='create_product'),
     path('account/update/product/<slug:slug>/', views.edit_product, name='edit_product'),
     path('account/delete/product/<slug:slug>/', views.delete_product, name='delete_product'),




     #BANNERS
     path('account/add-banner/', views.add_banner, name="add_banner"),
     path('account/banners/update/<str:pk>/', views.update_banner, name='update_banner'),
     path('account/banners/delete/<str:pk>/', views.delete_banner, name='delete_banner'),
     path('account/banners/', views.banners, name="banners"),


     path('account/orders/', views.orders, name="orders"),
     path('account/order-details/', views.order_details, name="order_details"),





     path('account/customers/', customer_list, name='customer_list'),
     path('account/customers/<int:user_id>/', customer_detail, name='customer_detail'),



     path('account/payments/', views.payments, name="payments"),

     path('account/video-products/', views.video_products_list, name="video_products_list"),
     path('account/video-products/create/', views.create_video_product, name="create_video_product"),
     path('account/video-products/edit/<int:pk>/', views.edit_video_product, name="edit_video_product"),
     path('account/video-products/delete/<int:pk>/', views.delete_video_product, name="delete_video_product"),

     # gallery
     path('account/gallery/', views.gallery, name="gallery"),
     path('account/add-gallery/', views.add_gallery, name="add_gallery"),
     path('account/gallery/delete/<str:pk>/', views.delete_gallery, name='delete_gallery'),

     # scrolling images
     path('account/scrolling-images/', views.scrolling_images, name="scrolling_images"),
     path('account/add-scrolling/', views.add_scrolling_images, name="add_scrolling_images"),
     path('account/scrolling-images/delete/<str:pk>/', views.delete_scrolling_images, name='delete_scrolling_images'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)