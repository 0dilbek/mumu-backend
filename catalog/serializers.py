from rest_framework import serializers

from .models import (
    AttributeDefinition,
    AttributeOption,
    Brand,
    Category,
    Product,
    ProductAttributeValue,
    ProductMedia,
    ProductType,
    ProductVariant,
    VariantAttributeValue,
)


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'image',
            'sort_order', 'is_active', 'children',
        )

    def get_children(self, obj):
        qs = obj.children.filter(is_active=True).order_by('sort_order', 'name')
        return CategoryTreeSerializer(qs, many=True).data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id', 'parent', 'name', 'slug', 'description', 'image',
            'is_active', 'sort_order', 'seo_title', 'seo_description',
        )


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ('id', 'name', 'slug', 'description', 'is_active')


class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = ('id', 'value', 'label', 'slug', 'sort_order')


class AttributeDefinitionSerializer(serializers.ModelSerializer):
    options = AttributeOptionSerializer(many=True, read_only=True)

    class Meta:
        model = AttributeDefinition
        fields = (
            'id', 'name', 'code', 'data_type', 'unit',
            'is_required', 'is_filterable', 'is_searchable',
            'is_variant_level', 'is_public', 'sort_order',
            'help_text', 'options',
        )


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'logo', 'description', 'country', 'is_active')


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = ('id', 'media_type', 'url', 'alt_text', 'sort_order', 'is_primary')


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_code = serializers.CharField(source='attribute.code', read_only=True)
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    attribute_type = serializers.CharField(source='attribute.data_type', read_only=True)
    display_value = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttributeValue
        fields = (
            'attribute', 'attribute_code', 'attribute_name', 'attribute_type',
            'value_text', 'value_number', 'value_decimal',
            'value_boolean', 'value_date', 'value_json', 'option',
            'display_value',
        )

    def get_display_value(self, obj):
        return obj.get_value()


class VariantAttributeValueSerializer(serializers.ModelSerializer):
    attribute_code = serializers.CharField(source='attribute.code', read_only=True)
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    display_value = serializers.SerializerMethodField()

    class Meta:
        model = VariantAttributeValue
        fields = (
            'attribute', 'attribute_code', 'attribute_name',
            'value_text', 'value_number', 'value_decimal',
            'value_boolean', 'value_date', 'value_json', 'option',
            'display_value',
        )

    def get_display_value(self, obj):
        return obj.get_value()


class ProductVariantSerializer(serializers.ModelSerializer):
    attribute_values = VariantAttributeValueSerializer(many=True, read_only=True)
    media = ProductMediaSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = (
            'id', 'sku', 'barcode', 'name', 'slug',
            'price', 'compare_at_price', 'currency',
            'weight', 'status', 'is_default',
            'attribute_values', 'media',
        )


class ProductListSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_category_name = serializers.CharField(source='primary_category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'short_description', 'status',
            'brand_name', 'primary_category_name',
            'primary_image', 'min_price',
        )

    def get_primary_image(self, obj):
        media = obj.media.filter(is_primary=True, media_type='image').first()
        if not media:
            media = obj.media.filter(media_type='image').first()
        return media.url if media else None

    def get_min_price(self, obj):
        variant = obj.variants.filter(status='active').order_by('price').first()
        return str(variant.price) if variant else None


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)
    primary_category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    media = ProductMediaSerializer(many=True, read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'short_description',
            'status', 'product_type', 'brand', 'primary_category',
            'categories', 'variants', 'media', 'attribute_values',
            'seo_title', 'seo_description',
            'created_at', 'updated_at',
        )

    def get_categories(self, obj):
        return [
            {'id': pc.category.id, 'name': pc.category.name, 'slug': pc.category.slug}
            for pc in obj.product_categories.select_related('category').all()
        ]


class FilterMetaSerializer(serializers.Serializer):
    category_id = serializers.IntegerField(read_only=True)
    category_slug = serializers.CharField(read_only=True)
    filters = serializers.ListField(read_only=True)
