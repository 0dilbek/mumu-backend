from django.db.models import Min, Q
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    AttributeDefinition,
    Brand,
    Category,
    Product,
    ProductType,
    ProductVariant,
)
from .serializers import (
    AttributeDefinitionSerializer,
    BrandSerializer,
    CategorySerializer,
    CategoryTreeSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductTypeSerializer,
    ProductVariantSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True).select_related('parent')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=False, url_path='tree')
    def tree(self, request):
        roots = Category.objects.filter(parent=None, is_active=True).order_by('sort_order', 'name')
        serializer = CategoryTreeSerializer(roots, many=True)
        return Response(serializer.data)


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductType.objects.filter(is_active=True)
    serializer_class = ProductTypeSerializer
    lookup_field = 'slug'


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductListSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'short_description', 'brand__name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = (
            Product.objects
            .filter(status='active')
            .select_related('brand', 'primary_category', 'product_type')
            .prefetch_related('media', 'variants')
        )

        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(
                Q(primary_category__slug=category_slug) |
                Q(product_categories__category__slug=category_slug)
            ).distinct()

        brand_slug = self.request.query_params.get('brand')
        if brand_slug:
            qs = qs.filter(brand__slug=brand_slug)

        product_type_slug = self.request.query_params.get('product_type')
        if product_type_slug:
            qs = qs.filter(product_type__slug=product_type_slug)

        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min or price_max:
            qs = qs.annotate(min_price=Min('variants__price'))
            if price_min:
                qs = qs.filter(min_price__gte=price_min)
            if price_max:
                qs = qs.filter(min_price__lte=price_max)

        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            qs = qs.filter(variants__status='active').distinct()

        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_object(self):
        qs = (
            Product.objects
            .select_related('brand', 'primary_category', 'product_type')
            .prefetch_related(
                'variants__attribute_values__attribute',
                'variants__attribute_values__option',
                'variants__media',
                'media',
                'attribute_values__attribute',
                'attribute_values__option',
                'product_categories__category',
            )
        )
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        return qs.get(**filter_kwargs)

    @action(detail=True, url_path='variants')
    def variants(self, request, slug=None):
        product = self.get_object()
        variants = product.variants.filter(status='active').prefetch_related(
            'attribute_values__attribute', 'attribute_values__option', 'media'
        )
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)


class FilterMetaViewSet(viewsets.ViewSet):
    """
    GET /api/filters/?category=<slug>
    Kategoriya bo'yicha filterlash uchun attribute definition'larni qaytaradi.
    """

    def list(self, request):
        category_slug = request.query_params.get('category')
        if not category_slug:
            return Response(
                {'detail': 'category query param talab qilinadi.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return Response(
                {'detail': 'Kategoriya topilmadi.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        product_types = ProductType.objects.filter(
            products__product_categories__category=category,
            is_active=True,
        ).distinct()

        attrs = (
            AttributeDefinition.objects
            .filter(product_type__in=product_types, is_filterable=True)
            .prefetch_related('options')
            .order_by('sort_order', 'name')
        )
        serializer = AttributeDefinitionSerializer(attrs, many=True)
        return Response({
            'category': {'id': category.id, 'name': category.name, 'slug': category.slug},
            'filters': serializer.data,
        })
