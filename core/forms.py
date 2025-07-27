from django import forms
from .models import *
from .models import Product
from tinymce.widgets import TinyMCE
from taggit.forms import TagWidget
from multiselectfield import MultiSelectFormField
from django.forms import inlineformset_factory
from .models import VideoProduct





class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'email', 'gender',]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.filter(email=email).exclude(user=self.instance.user).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

STATUS_CHOICES = [
    (True, 'Active'),
    (False, 'Inactive')
]



class BannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        fields = [
            'heading',
            'description',
            'button_text',
            'button_url',
            'image_for_desktop',
            'image_for_mobile',
            'status',
            'color'
        ]
        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES),
            'image_for_desktop': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                "accept": "image/*"
            }),
            'image_for_mobile': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                "accept": "image/*"
            }),
        }





    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['heading'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control description_class'
        self.fields['button_text'].widget.attrs['class'] = 'form-control'
        self.fields['color'].widget.attrs['class'] = 'form-control'
        self.fields['button_url'].widget.attrs['class'] = 'form-control'


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['image', 'description']  # Include description

        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                'accept': 'image/*',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter image description',
                'required': 'required',
            }),
        }

class ScrollingImagesForm(forms.ModelForm):
    class Meta:
        model = ScrollingImages
        fields = ['image']

        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'file__input',
                'required': 'required',
                "accept": "image/*"
            }),
        }



class VideoProductForm(forms.ModelForm):
    class Meta:
        model = VideoProduct
        fields = ['name', 'description', 'video', 'product_image', 'product_url','actual_price', 'current_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        actual_price = cleaned_data.get('actual_price')
        current_price = cleaned_data.get('current_price')
        
        if actual_price and current_price and current_price > actual_price:
            raise forms.ValidationError("Current price cannot be higher than actual price.")
        return cleaned_data







class VideoProductForm(forms.ModelForm):
    class Meta:
        model = VideoProduct
        fields = ['name', 'description', 'video', 'product_image', 'product_url','actual_price', 'current_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        actual_price = cleaned_data.get('actual_price')
        current_price = cleaned_data.get('current_price')
        
        if actual_price and current_price and current_price > actual_price:
            raise forms.ValidationError("Current price cannot be higher than actual price.")
        return cleaned_data




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','priority', 'slug', 'image', 'parent_category', 'description', 'status']






class ProductForm(forms.ModelForm):
    description = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 10, 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'name', 'image', 'category', 'price',
            'discounted_price', 'in_stock', 'status', 'tags',
            'description', 'color', 'available_sizes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discounted_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'in_stock': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'tags': TagWidget(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'available_sizes': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ('image',)
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class AccordionForm(forms.ModelForm):
    class Meta:
        model = Accordion
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': TinyMCE(attrs={'cols': 80, 'rows': 5, 'class': 'form-control'}),
        }

# Create formsets for related models
ProductImageFormSet = inlineformset_factory(
    Product, ProductImage,
    form=ProductImageForm,
    extra=1,
    can_delete=True
)

AccordionFormSet = inlineformset_factory(
    Product, Accordion, 
    form=AccordionForm,
    extra=1,
    can_delete=True
)


