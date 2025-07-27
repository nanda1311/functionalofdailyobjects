from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages as toast
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProductForm,VideoProductForm
from .forms import *
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.utils.text import slugify
from decimal import Decimal, InvalidOperation
from .models import ScrollingImages
from django.forms import modelformset_factory, inlineformset_factory
from .models import Product, ProductImage, Cart,Profile,VideoProduct
from django.db import transaction
import datetime






def signup_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if password != confirm_password:
            toast.error(request, "Passwords do not match")
            return render(request, 'frontend/signup.html')  # your template

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                )

                Profile.objects.create(
                    user=user,
                    name=name,
                    gender=gender[0].upper(),  # 'm' -> 'M'
                    phone_number=mobile,
                    email=email,
                )

                toast.success(request, "Account created successfully! Please log in.")
                return redirect('signin')  # your login URL name
        except Exception as e:
            toast.error(request, f"Error: {str(e)}")
            return render(request, 'frontend/signup.html')  # re-render with error

    return render(request, 'frontend/signup.html')


def signin_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            toast.success(request, "Logged in successfully.")
            return redirect('home')
        else:
            toast.error(request, 'Invalid credentials.')

    return render(request, 'frontend/signin.html')




def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('dashboard')
        else:
            toast.error(request, "Access denied. Superuser only.")
            return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                auth_login(request, user)
                toast.success(request, "Logged in successfully.")
                return redirect('dashboard')
            else:
                toast.error(request, "Only superusers can access this page.")
                return redirect('login')
        else:
            toast.error(request, 'Invalid credentials.')

    return render(request, 'backend/login.html')




def signout(request):
    logout(request)
    return redirect('signin')








def video_products_list(request):
    video = VideoProduct.objects.all().order_by('-created_at')
    context = {'video': video}
    return render(request, 'backend/video_products/list.html', context)


def create_video_product(request):
    if request.method == 'POST':
        form = VideoProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            toast.success(request, 'Video product created successfully!')
            return redirect('video_products_list')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    toast.error(request, f"{field}: {error}")
    else:
        form = VideoProductForm()
    
    context = {'form': form, 'title': 'Create Video Product'}
    return render(request, 'backend/video_products/form.html', context)

def edit_video_product(request, pk):
    product = get_object_or_404(VideoProduct, pk=pk)
    if request.method == 'POST':
        form = VideoProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            toast.add_message(request, toast.SUCCESS, 'Video product updated successfully!')
            return redirect('video_products_list')
        else:
            toast.add_message(request, toast.ERROR, 'Please correct the errors below.')
    else:
        form = VideoProductForm(instance=product)
    
    context = {'form': form, 'title': 'Edit Video Product'}
    return render(request, 'backend/video_products/form.html', context)

def delete_video_product(request, pk):
    product = get_object_or_404(VideoProduct, pk=pk)
    if request.method == 'POST':
        product.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)





# FRONTEND

def home(request):
    scrolling_images = ScrollingImages.objects.all()  # Get all scrolling images
    categories=Category.objects.all().order_by('-priority')
    new_arrivals = Product.objects.all().order_by('-created_at')[:3]
    banners= Banner.objects.all()
    products = Product.objects.all()
    video = VideoProduct.objects.all()

    return render(request, 'frontend/index.html', {
        'scrolling_images': scrolling_images,
        'categories':categories, 
        'new_arrivals': new_arrivals,
        'banners':banners, 
        'products': products,
        'video': video
        

    })



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    print(product)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        toast.success(request, "Quantity updated in cart.")
    else:
        toast.success(request, "Product added to cart.")

    return redirect('cart')  # Replace with your cart view name





@login_required
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart = request.session.get('cart', {})
        
        if action == 'increase':
            cart[item_id] = cart.get(item_id, 0) + 1
        elif action == 'decrease':
            if cart.get(item_id, 0) > 1:
                cart[item_id] -= 1
            else:
                del cart[item_id]
        elif action == 'remove':
            if item_id in cart:
                del cart[item_id]
        
        request.session['cart'] = cart
        request.session.modified = True
    
    return redirect('cart')

def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.product.discounted_price * item.quantity for item in cart_items)

    return render(request, 'frontend/cart.html', {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
    })


def artist_page(request):
    galleries = Gallery.objects.all()
    return render(request, 'frontend/artist-page.html', {'galleries': galleries})





def shop(request):
    products = Product.objects.filter(status='active').order_by('-created_at')
    categories = Category.objects.all() 

    return render(request, 'frontend/shop.html', {
        'products': products,
        'categories': categories
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.prefetch_related('accordions'), slug=slug)
    categories = Category.objects.all() 
    context = {
        'categories': categories,
        'product': product
    }
    return render(request, 'frontend/product-detail.html', context)



def cateogry_products(request, slug):
    categories = Category.objects.all()
    category = Category.objects.get(slug=slug)
    products = Product.objects.filter(category = category)
    context = {
        'category': category,
        'products': products,
        'categories': categories
    }
    return render(request, 'frontend/category-products.html', context)


ProductImageFormSet = inlineformset_factory(
    Product, ProductImage,
    fields=('image',),
    extra=3,
    can_delete=True
)





# logout
@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')




# BACKEND
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'backend/index.html')

@login_required(login_url='login')
def categories(request):
    # notifications_list = Notification.objects.filter(read_status = False).order_by('-created_at')

    categories = Category.objects.all().order_by('-created_at')
    category_slug = request.GET.get('edit') or request.GET.get('delete')
    print(category_slug)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
    else:
        category = None

    print(request.POST)

    if request.method == 'POST':
        print(request.POST)
        if 'slug' in request.POST:
            form = CategoryForm(request.POST, request.FILES, instance=category)
        else:
            form = CategoryForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            toast.success(request, 'Category updated successfully!' if category else 'Category created successfully!')
            return redirect('categories')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(error)
                    toast.error(request, f"{field}: {error}")
            toast.error(request, 'Please correct the errors below.')

    elif request.method == 'GET' and category and 'delete' in request.GET:
        category.delete()
        toast.success(request, 'Category deleted successfully!')
        return redirect('categories')

    else:
        form = CategoryForm(instance=category)

    return render(request, 'backend/categories.html', {
        'form': form,
        'categories': categories,
        'edit_mode': bool(category),
    })


def admin_logout(request):
    logout(request)
    return redirect('login')



@login_required(login_url='login')
def products(request):
    product_list = Product.objects.all()
    return render(request, 'backend/products.html', {'products': product_list})



@login_required(login_url='login')
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        image_formset = ProductImageFormSet(request.POST, request.FILES, prefix='images')
        accordion_formset = AccordionFormSet(request.POST, prefix='accordions')
        
        if form.is_valid() and image_formset.is_valid() and accordion_formset.is_valid():
            product = form.save()
            
            # Save images
            image_formset.instance = product
            image_formset.save()
            
            # Save accordions
            accordion_formset.instance = product
            accordion_formset.save()
            
            toast.success(request, 'Product created successfully.')
            return redirect('products')
        else:
            print(form.errors)
            toast.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
        image_formset = ProductImageFormSet(prefix='images')
        accordion_formset = AccordionFormSet(prefix='accordions')
    
    return render(request, 'backend/create-product.html', {
        'form': form,
        'image_formset': image_formset,
        'accordion_formset': accordion_formset,
    })



@login_required(login_url='login')
def edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        image_formset = ProductImageFormSet(
            request.POST, request.FILES, 
            instance=product,
            prefix='images'
        )
        accordion_formset = AccordionFormSet(
            request.POST,
            instance=product,
            prefix='accordions'
        )
        
        if form.is_valid() and image_formset.is_valid() and accordion_formset.is_valid():
            form.save()
            image_formset.save()
            accordion_formset.save()
            
            # Handle additional image uploads
            if 'additional_images' in request.FILES:
                for image in request.FILES.getlist('additional_images'):
                    ProductImage.objects.create(product=product, image=image)
            
            toast.success(request, 'Product updated successfully.')
            return redirect('products')
        else:
            toast.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
        image_formset = ProductImageFormSet(instance=product, prefix='images')
        accordion_formset = AccordionFormSet(instance=product, prefix='accordions')
    
    return render(request, 'backend/edit-product.html', {
        'form': form,
        'product': product,
        'image_formset': image_formset,
        'accordion_formset': accordion_formset
    })

@login_required(login_url='login')
def delete_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        product.delete()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})

@login_required(login_url='login')
def add_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            toast.success(request, "Banner Created Successfully")
            return redirect('banners')
        else:
            print(form.errors)  # Fixed the typo here
            toast.error(request, 'Failed to Create banner. Please check the form for errors.')
    form = BannerForm()
    context = {
        'form': form
    }
    return render(request, 'backend/add-banners.html', context)


@login_required(login_url='login')
def banners(request):
    banners = Banner.objects.all()
    context = {'banners': banners}
    return render(request, 'backend/banners.html',context)



@login_required(login_url='login')
def update_banner(request, pk):
    banner = get_object_or_404(Banner, id=pk)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            toast.success(request, 'Banner Updated Successfully')
            return redirect('banners')
        else:
            toast.error(request, 'Failed to update banner. Please check the form for errors.')
    else:
        form = BannerForm(instance=banner)
    return render(request, 'backend/update-banner.html', {'form': form, 'banner': banner})



@login_required(login_url='login')
def delete_banner(request, pk):
    try:
        banner = Banner.objects.get(pk=pk)
        banner.delete()
        toast.success(request, 'Banner deleted successfully.')
        return redirect('banners')
    except Banner.DoesNotExist:
        toast.error(request, 'Banner not found.')
        return redirect('banners')



@login_required(login_url='login')
def customer_list(request):
    customers = Profile.objects.select_related('user').all()
    return render(request, 'backend/customer_list.html', {'customers': customers})

@login_required(login_url='login')
def customer_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    # wishlist_items = Wishlist.objects.filter(user=user)
    # cart_items = CartItem.objects.filter(user=user)
    # orders = Order.objects.filter(user=user)

    context = {
        'user': user,
        'profile': profile,
        # 'wishlist_items': wishlist_items,
        # 'cart_items': cart_items,
        # 'orders': orders,
    }
    return render(request, 'backend/customer_detail.html', context)










@login_required(login_url='login')
def orders(request):
    return render(request, 'backend/orders.html')

@login_required(login_url='login')
def order_details(request):
    return render(request, 'backend/order-details.html')

@login_required(login_url='login')
def sellers(request):
    return render(request, 'backend/sellers.html')

@login_required(login_url='login')
def seller_details(request):
    return render(request, 'backend/seller-details.html')

# message view 
@login_required(login_url='login')
def messages(request):
   
    inbox = Message.objects.all().order_by('-created_at')
    inbox_count = Message.objects.all().count()
    now = datetime.datetime.now().strftime('%I:%M %p')
    context = {'inbox': inbox, 'now':now, 'inbox_count': inbox_count}
    return render(request, 'backend/messages.html', context)




@login_required(login_url='login')
def view_messages(request):
    return render(request, 'backend/view-toast.html')

@login_required(login_url='login')
def payments(request):
    return render(request, 'backend/payments.html')

@login_required(login_url='login')
def gallery(request):

    galleries = Gallery.objects.all()
    context = {
        'galleries': galleries
    }

    return render(request, 'backend/gallery.html', context)

@login_required(login_url='login')
def add_gallery(request):
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            toast.success(request, " Image Added Successfully")
            return redirect('gallery')
        else:
           toast.error(request, 'Failed to Add Image. Please check the form for errors.')

    form = GalleryForm()
    context = {
        'form': form
    }
    return render(request, 'backend/add-gallery.html', context)




@login_required(login_url='login')
def delete_gallery(request, pk):
    try:
        gallery = Gallery.objects.get(id=pk)
        gallery.delete()
        toast.success(request, 'image deleted successfully.')
        return redirect('gallery')
    except Gallery.DoesNotExist:
        toast.error(request, 'image not found.')
        return redirect('gallery')





@login_required(login_url='login')
def scrolling_images(request):
    
    scrolling_images = ScrollingImages.objects.all()
    context = {
        'scrolling_images': scrolling_images
    }
    return render(request, 'backend/scrolling-images.html', context)




@login_required(login_url='login')
def add_scrolling_images(request):
    if request.method == 'POST':
        form = ScrollingImagesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            toast.success(request, " Scrolling Image Added Successfully")
            return redirect('scrolling_images')
        else:
           toast.error(request, 'Failed to Add Image. Please check the form for errors.')

    form = ScrollingImagesForm()
    context = {
        'form': form
    }
    return render(request, 'backend/add-scroll.html', context)




def delete_scrolling_images(request, pk):  # Change from id to pk
    image = get_object_or_404(ScrollingImages, id=pk)
    image.delete()
    return redirect('scrolling_images')
