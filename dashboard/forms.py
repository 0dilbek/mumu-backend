from django import forms
from django.forms import inlineformset_factory

from catalog.models import (
    AttributeDefinition,
    AttributeOption,
    Brand,
    Category,
    Product,
    ProductMedia,
    ProductType,
    ProductVariant,
)

_CTRL = {'class': 'form-control'}
_SEL  = {'class': 'form-select'}
_SM   = {'class': 'form-control form-control-sm'}
_SEL_SM = {'class': 'form-select form-select-sm'}
_CHK  = {'class': 'form-check-input'}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'product_type', 'brand', 'primary_category',
            'status', 'short_description', 'description',
            'seo_title', 'seo_description',
        ]
        widgets = {
            'name':              forms.TextInput(attrs={**_CTRL, 'placeholder': 'Masalan: Royal Canin Mini Adult'}),
            'slug':              forms.TextInput(attrs={**_CTRL, 'placeholder': 'royal-canin-mini-adult'}),
            'product_type':      forms.Select(attrs=_SEL),
            'brand':             forms.Select(attrs=_SEL),
            'primary_category':  forms.Select(attrs=_SEL),
            'status':            forms.Select(attrs=_SEL),
            'short_description': forms.Textarea(attrs={**_CTRL, 'rows': 2, 'placeholder': 'Qisqa tavsif (1-2 jumla)'}),
            'description':       forms.Textarea(attrs={**_CTRL, 'rows': 6}),
            'seo_title':         forms.TextInput(attrs=_CTRL),
            'seo_description':   forms.Textarea(attrs={**_CTRL, 'rows': 2}),
        }


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'sku', 'barcode', 'price', 'compare_at_price', 'status', 'is_default']
        widgets = {
            'name':             forms.TextInput(attrs={**_SM, 'placeholder': '2kg yoki Qizil-L'}),
            'sku':              forms.TextInput(attrs={**_SM, 'placeholder': 'SKU-001'}),
            'barcode':          forms.TextInput(attrs=_SM),
            'price':            forms.NumberInput(attrs={**_SM, 'step': '1', 'placeholder': '0'}),
            'compare_at_price': forms.NumberInput(attrs={**_SM, 'step': '1', 'placeholder': '0'}),
            'status':           forms.Select(attrs=_SEL_SM),
            'is_default':       forms.CheckboxInput(attrs=_CHK),
        }


class ProductMediaForm(forms.ModelForm):
    class Meta:
        model = ProductMedia
        fields = ['url', 'alt_text', 'media_type', 'sort_order', 'is_primary']
        widgets = {
            'url':        forms.URLInput(attrs={**_SM, 'placeholder': 'https://...'}),
            'alt_text':   forms.TextInput(attrs={**_SM, 'placeholder': 'Rasm tavsifi'}),
            'media_type': forms.Select(attrs=_SEL_SM),
            'sort_order': forms.NumberInput(attrs={**_SM, 'style': 'width:70px'}),
            'is_primary': forms.CheckboxInput(attrs=_CHK),
        }


VariantFormSet = inlineformset_factory(
    Product, ProductVariant,
    form=ProductVariantForm,
    extra=1, can_delete=True,
    fields=['name', 'sku', 'barcode', 'price', 'compare_at_price', 'status', 'is_default'],
)

MediaFormSet = inlineformset_factory(
    Product, ProductMedia,
    form=ProductMediaForm,
    extra=1, can_delete=True,
    fields=['url', 'alt_text', 'media_type', 'sort_order', 'is_primary'],
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['parent', 'name', 'slug', 'description', 'image', 'sort_order', 'is_active', 'seo_title', 'seo_description']
        widgets = {
            'parent':          forms.Select(attrs=_SEL),
            'name':            forms.TextInput(attrs=_CTRL),
            'slug':            forms.TextInput(attrs=_CTRL),
            'description':     forms.Textarea(attrs={**_CTRL, 'rows': 3}),
            'image':           forms.URLInput(attrs={**_CTRL, 'placeholder': 'https://...'}),
            'sort_order':      forms.NumberInput(attrs={**_CTRL, 'style': 'width:100px'}),
            'is_active':       forms.CheckboxInput(attrs=_CHK),
            'seo_title':       forms.TextInput(attrs=_CTRL),
            'seo_description': forms.Textarea(attrs={**_CTRL, 'rows': 2}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'slug', 'logo', 'description', 'country', 'is_active']
        widgets = {
            'name':        forms.TextInput(attrs=_CTRL),
            'slug':        forms.TextInput(attrs=_CTRL),
            'logo':        forms.URLInput(attrs={**_CTRL, 'placeholder': 'https://...'}),
            'description': forms.Textarea(attrs={**_CTRL, 'rows': 3}),
            'country':     forms.TextInput(attrs=_CTRL),
            'is_active':   forms.CheckboxInput(attrs=_CHK),
        }


class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ['name', 'slug', 'description', 'is_active']
        widgets = {
            'name':        forms.TextInput(attrs=_CTRL),
            'slug':        forms.TextInput(attrs=_CTRL),
            'description': forms.Textarea(attrs={**_CTRL, 'rows': 3}),
            'is_active':   forms.CheckboxInput(attrs=_CHK),
        }


class AttributeDefinitionForm(forms.ModelForm):
    class Meta:
        model = AttributeDefinition
        fields = ['name', 'code', 'data_type', 'unit', 'is_required', 'is_filterable', 'is_searchable', 'is_variant_level', 'sort_order', 'help_text']
        widgets = {
            'name':             forms.TextInput(attrs=_CTRL),
            'code':             forms.TextInput(attrs={**_CTRL, 'placeholder': 'masalan: protein_percent'}),
            'data_type':        forms.Select(attrs=_SEL),
            'unit':             forms.TextInput(attrs={**_CTRL, 'placeholder': 'kg, %, cm ...'}),
            'sort_order':       forms.NumberInput(attrs=_CTRL),
            'help_text':        forms.TextInput(attrs=_CTRL),
            'is_required':      forms.CheckboxInput(attrs=_CHK),
            'is_filterable':    forms.CheckboxInput(attrs=_CHK),
            'is_searchable':    forms.CheckboxInput(attrs=_CHK),
            'is_variant_level': forms.CheckboxInput(attrs=_CHK),
        }


class AttributeOptionForm(forms.ModelForm):
    class Meta:
        model = AttributeOption
        fields = ['label', 'value', 'slug', 'sort_order', 'is_active']
        widgets = {
            'label':      forms.TextInput(attrs={**_SM, 'placeholder': "Ko'rsatiladigan nom"}),
            'value':      forms.TextInput(attrs={**_SM, 'placeholder': 'ichki qiymat'}),
            'slug':       forms.TextInput(attrs=_SM),
            'sort_order': forms.NumberInput(attrs={**_SM, 'style': 'width:70px'}),
            'is_active':  forms.CheckboxInput(attrs=_CHK),
        }
