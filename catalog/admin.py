from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AttributeDefinition,
    AttributeOption,
    Brand,
    Category,
    Product,
    ProductAttributeValue,
    ProductCategory,
    ProductMedia,
    ProductType,
    ProductVariant,
    VariantAttributeValue,
)


# ─── Inlines ──────────────────────────────────────────────────────────────────

class CategoryChildInline(admin.TabularInline):
    model = Category
    fk_name = 'parent'
    extra = 0
    fields = ('name', 'slug', 'sort_order', 'is_active')
    show_change_link = True


class AttributeDefinitionInline(admin.TabularInline):
    model = AttributeDefinition
    extra = 1
    fields = (
        'name', 'code', 'data_type', 'unit',
        'is_required', 'is_filterable', 'is_variant_level', 'sort_order',
    )
    show_change_link = True


class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption
    extra = 2
    fields = ('label', 'value', 'slug', 'sort_order', 'is_active')


class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory
    extra = 1
    fields = ('category', 'is_primary', 'sort_order')
    autocomplete_fields = ['category']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        'name', 'sku', 'price', 'compare_at_price',
        'status', 'is_default', 'barcode',
    )
    show_change_link = True


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    fields = ('url', 'alt_text', 'media_type', 'sort_order', 'is_primary')


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 0
    fields = (
        'attribute', 'value_text', 'value_number', 'value_decimal',
        'value_boolean', 'option',
    )
    autocomplete_fields = ['attribute', 'option']


class VariantAttributeValueInline(admin.TabularInline):
    model = VariantAttributeValue
    extra = 0
    fields = (
        'attribute', 'value_text', 'value_number', 'value_decimal',
        'value_boolean', 'option',
    )
    autocomplete_fields = ['attribute', 'option']


# ─── Category ─────────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'parent', 'sort_order', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('sort_order', 'is_active')
    ordering = ('parent__name', 'sort_order', 'name')
    inlines = [CategoryChildInline]
    fieldsets = (
        (None, {
            'fields': ('parent', 'name', 'slug', 'description', 'image'),
        }),
        ('Tartib va holat', {
            'fields': ('sort_order', 'is_active'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description'),
        }),
    )


# ─── ProductType + AttributeDefinition ────────────────────────────────────────

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'attribute_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AttributeDefinitionInline]

    def attribute_count(self, obj):
        return obj.attributes.count()
    attribute_count.short_description = 'Xususiyatlar'


@admin.register(AttributeDefinition)
class AttributeDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'product_type', 'data_type', 'unit',
        'is_required', 'is_filterable', 'is_variant_level',
    )
    list_filter = ('product_type', 'data_type', 'is_filterable', 'is_variant_level')
    search_fields = ('name', 'code', 'product_type__name')
    autocomplete_fields = ['product_type']
    inlines = [AttributeOptionInline]
    fieldsets = (
        (None, {
            'fields': ('product_type', 'name', 'code', 'data_type', 'unit', 'help_text'),
        }),
        ('Parametrlar', {
            'fields': (
                'is_required', 'is_filterable', 'is_searchable',
                'is_variant_level', 'is_public', 'sort_order',
            ),
        }),
        ('Validatsiya qoidalari (JSON)', {
            'classes': ('collapse',),
            'fields': ('validation_rules',),
        }),
    )


@admin.register(AttributeOption)
class AttributeOptionAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'slug', 'attribute', 'sort_order', 'is_active')
    list_filter = ('attribute__product_type', 'is_active')
    search_fields = ('label', 'value', 'attribute__name')
    autocomplete_fields = ['attribute']
    prepopulated_fields = {'slug': ('value',)}


# ─── Brand ────────────────────────────────────────────────────────────────────

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'country', 'is_active', 'logo_preview')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:30px;">', obj.logo)
        return '—'
    logo_preview.short_description = 'Logo'


# ─── Product ──────────────────────────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'status', 'product_type', 'brand',
        'primary_category', 'variant_count', 'created_at',
    )
    list_filter = ('status', 'product_type', 'brand', 'primary_category')
    search_fields = ('name', 'slug', 'brand__name')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['product_type', 'brand', 'primary_category']
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    inlines = [
        ProductCategoryInline,
        ProductVariantInline,
        ProductMediaInline,
        ProductAttributeValueInline,
    ]
    fieldsets = (
        (None, {
            'fields': (
                'name', 'slug', 'product_type', 'brand',
                'primary_category', 'status',
            ),
        }),
        ('Tavsif', {
            'fields': ('short_description', 'description'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description'),
        }),
    )

    def variant_count(self, obj):
        return obj.variants.count()
    variant_count.short_description = 'Variantlar'


# ─── ProductVariant ───────────────────────────────────────────────────────────

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'sku', 'price', 'compare_at_price',
        'currency', 'status', 'is_default',
    )
    list_filter = ('status', 'currency', 'product__product_type')
    search_fields = ('sku', 'barcode', 'name', 'product__name')
    autocomplete_fields = ['product']
    list_editable = ('price', 'status')
    inlines = [VariantAttributeValueInline, ProductMediaInline]
    fieldsets = (
        (None, {
            'fields': ('product', 'name', 'slug', 'sku', 'barcode'),
        }),
        ('Narx', {
            'fields': ('price', 'compare_at_price', 'cost_price', 'currency'),
        }),
        ('Holat', {
            'fields': ('status', 'is_default', 'weight'),
        }),
    )


# ─── ProductMedia ─────────────────────────────────────────────────────────────

@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'media_type', 'is_primary', 'sort_order', 'image_preview')
    list_filter = ('media_type', 'is_primary')
    search_fields = ('product__name', 'variant__sku', 'alt_text')
    autocomplete_fields = ['product', 'variant']

    def image_preview(self, obj):
        if obj.media_type == 'image' and obj.url:
            return format_html('<img src="{}" style="height:40px;">', obj.url)
        return '—'
    image_preview.short_description = 'Preview'
