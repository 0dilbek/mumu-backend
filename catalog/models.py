from django.db import models


class Category(models.Model):
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    image = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        indexes = [
            models.Index(fields=['parent', 'sort_order']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        if self.parent:
            return f'{self.parent} → {self.name}'
        return self.name

    def get_ancestors(self):
        ancestors = []
        node = self.parent
        while node:
            ancestors.insert(0, node)
            node = node.parent
        return ancestors


class ProductType(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Mahsulot turi'
        verbose_name_plural = 'Mahsulot turlari'

    def __str__(self):
        return self.name


class AttributeDefinition(models.Model):
    DATA_TYPE_CHOICES = [
        ('text', 'Matn'),
        ('number', 'Butun son'),
        ('decimal', "O'nlik son"),
        ('boolean', "Ha/Yo'q"),
        ('enum', 'Enum (bitta tanlov)'),
        ('multi_enum', "Multi-enum (ko'p tanlov)"),
        ('date', 'Sana'),
        ('dimension', "O'lcham"),
        ('weight', 'Vazn'),
    ]

    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name='attributes'
    )
    name = models.CharField(max_length=200)
    code = models.SlugField(max_length=100)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    unit = models.CharField(max_length=20, blank=True, help_text='kg, g, cm, ml, % ...')
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=False)
    is_searchable = models.BooleanField(default=False)
    is_variant_level = models.BooleanField(
        default=False,
        help_text="True bo'lsa variantga, False bo'lsa productga tegishli"
    )
    is_public = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    validation_rules = models.JSONField(default=dict, blank=True)
    help_text = models.TextField(blank=True)

    class Meta:
        verbose_name = "Xususiyat ta'rifi"
        verbose_name_plural = "Xususiyat ta'riflari"
        unique_together = [['product_type', 'code']]
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f'{self.product_type.name} — {self.name} ({self.code})'


class AttributeOption(models.Model):
    attribute = models.ForeignKey(
        AttributeDefinition, on_delete=models.CASCADE, related_name='options'
    )
    value = models.CharField(max_length=200)
    label = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Xususiyat varianti'
        verbose_name_plural = 'Xususiyat variantlari'
        ordering = ['sort_order', 'label']

    def __str__(self):
        return f'{self.attribute.name}: {self.label}'


class Brand(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.URLField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Brend'
        verbose_name_plural = 'Brendlar'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('active', 'Faol'),
        ('out_of_stock', "Stokda yo'q"),
        ('archived', 'Arxivlangan'),
    ]

    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name='products'
    )
    brand = models.ForeignKey(
        Brand, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='products'
    )
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    description = models.TextField(blank=True)
    short_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    primary_category = models.ForeignKey(
        Category, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='primary_products'
    )
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_categories'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='product_categories'
    )
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Mahsulot kategoriyasi'
        verbose_name_plural = 'Mahsulot kategoriyalari'
        unique_together = [['product', 'category']]

    def __str__(self):
        return f'{self.product.name} → {self.category.name}'


class ProductVariant(models.Model):
    STATUS_CHOICES = [
        ('active', 'Faol'),
        ('inactive', 'Nofaol'),
        ('out_of_stock', "Stokda yo'q"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants'
    )
    sku = models.CharField(max_length=200, unique=True)
    barcode = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=500, blank=True, help_text='Masalan: 2kg, Qizil-L')
    slug = models.SlugField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_at_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Chegirmadan oldingi narx'
    )
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Tannarx (ichki foydalanish uchun)'
    )
    currency = models.CharField(max_length=3, default='UZS')
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        help_text='Yetkazib berish uchun vazn (kg)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_default = models.BooleanField(
        default=False, help_text="Mahsulot sahifasida birinchi ko'rinadigan variant"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mahsulot varianti'
        verbose_name_plural = 'Mahsulot variantlari'
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['sku']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        if self.name:
            return f'{self.product.name} — {self.name}'
        return f'{self.product.name} [{self.sku}]'


class ProductMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Rasm'),
        ('video', 'Video'),
    ]

    product = models.ForeignKey(
        Product, null=True, blank=True,
        on_delete=models.CASCADE, related_name='media'
    )
    variant = models.ForeignKey(
        ProductVariant, null=True, blank=True,
        on_delete=models.CASCADE, related_name='media'
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    url = models.URLField(max_length=1000)
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Media fayl'
        verbose_name_plural = 'Media fayllar'
        ordering = ['sort_order']

    def __str__(self):
        target = self.product or self.variant
        return f'{target} — {self.media_type} #{self.sort_order}'


class ProductAttributeValue(models.Model):
    attribute = models.ForeignKey(
        AttributeDefinition, on_delete=models.CASCADE, related_name='product_values'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='attribute_values'
    )
    value_text = models.TextField(blank=True)
    value_number = models.IntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_json = models.JSONField(null=True, blank=True)
    option = models.ForeignKey(
        AttributeOption, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='product_values'
    )

    class Meta:
        verbose_name = 'Mahsulot xususiyat qiymati'
        verbose_name_plural = 'Mahsulot xususiyat qiymatlari'
        unique_together = [['attribute', 'product']]

    def __str__(self):
        return f'{self.product.name} — {self.attribute.name}'

    def get_value(self):
        dt = self.attribute.data_type
        if dt == 'text':
            return self.value_text
        if dt == 'number':
            return self.value_number
        if dt == 'decimal':
            return self.value_decimal
        if dt == 'boolean':
            return self.value_boolean
        if dt == 'date':
            return self.value_date
        if dt in ('enum', 'multi_enum'):
            return self.option.label if self.option else self.value_json
        return self.value_json or self.value_text


class VariantAttributeValue(models.Model):
    attribute = models.ForeignKey(
        AttributeDefinition, on_delete=models.CASCADE, related_name='variant_values'
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name='attribute_values'
    )
    value_text = models.TextField(blank=True)
    value_number = models.IntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_json = models.JSONField(null=True, blank=True)
    option = models.ForeignKey(
        AttributeOption, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='variant_values'
    )

    class Meta:
        verbose_name = 'Variant xususiyat qiymati'
        verbose_name_plural = 'Variant xususiyat qiymatlari'
        unique_together = [['attribute', 'variant']]

    def __str__(self):
        return f'{self.variant} — {self.attribute.name}'

    def get_value(self):
        dt = self.attribute.data_type
        if dt == 'text':
            return self.value_text
        if dt == 'number':
            return self.value_number
        if dt == 'decimal':
            return self.value_decimal
        if dt == 'boolean':
            return self.value_boolean
        if dt == 'date':
            return self.value_date
        if dt in ('enum', 'multi_enum'):
            return self.option.label if self.option else self.value_json
        return self.value_json or self.value_text
