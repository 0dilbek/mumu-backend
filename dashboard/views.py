from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from catalog.models import (
    AttributeDefinition,
    AttributeOption,
    Brand,
    Category,
    Product,
    ProductType,
    ProductVariant,
)
from .forms import (
    AttributeDefinitionForm,
    AttributeOptionForm,
    BrandForm,
    CategoryForm,
    MediaFormSet,
    ProductForm,
    ProductTypeForm,
    VariantFormSet,
)

staff_required = method_decorator(staff_member_required, name='dispatch')


def _dashboard_stats():
    return {
        'products':      Product.objects.count(),
        'active':        Product.objects.filter(status='active').count(),
        'draft':         Product.objects.filter(status='draft').count(),
        'categories':    Category.objects.count(),
        'brands':        Brand.objects.count(),
        'variants':      ProductVariant.objects.count(),
        'product_types': ProductType.objects.count(),
    }


# ─── Dashboard Home ────────────────────────────────────────────────────────────

@staff_required
class HomeView(View):
    def get(self, request):
        ctx = {
            'stats': _dashboard_stats(),
            'recent': Product.objects.select_related('brand', 'primary_category').order_by('-created_at')[:10],
        }
        return render(request, 'dashboard/home.html', ctx)


@staff_required
class MobilePreviewView(View):
    def _category_meta(self, category):
        name = category.name.lower()
        meta = {
            'icon': 'bi-grid',
            'tone': 'sage',
            'label': category.name,
        }

        pet_map = [
            (('it', 'dog', 'kuchuk', 'kuchukcha'), 'bi-hearts', 'amber'),
            (('mushuk', 'cat', 'kitten'), 'bi-moon-stars', 'mint'),
            (('baliq', 'fish', 'aquarium'), 'bi-water', 'blue'),
            (('qush', 'bird', 'parrot'), 'bi-feather', 'sky'),
            (('kemiruvchi', 'hamster', 'rabbit', 'quyon', 'small'), 'bi-circle', 'rose'),
            (('reptile', 'sudralib', 'toshbaqa', 'turtle'), 'bi-brightness-high', 'lime'),
        ]

        for keywords, icon, tone in pet_map:
            if any(keyword in name for keyword in keywords):
                meta['icon'] = icon
                meta['tone'] = tone
                break

        return meta

    def get(self, request):
        categories = list(
            Category.objects
            .filter(is_active=True)
            .annotate(product_count=Count('product_categories'))
            .order_by('parent__name', 'sort_order', 'name')
        )
        root_categories = [category for category in categories if category.parent_id is None]
        children_by_parent = {}
        for category in categories:
            if category.parent_id:
                children_by_parent.setdefault(category.parent_id, []).append(category)

        pet_categories = [
            {
                'object': category,
                'children': [
                    {
                        'object': child,
                        **self._category_meta(child),
                    }
                    for child in children_by_parent.get(category.id, [])
                ],
                **self._category_meta(category),
            }
            for category in root_categories
        ]

        products = (
            Product.objects
            .filter(status='active')
            .select_related('brand', 'primary_category', 'product_type')
            .prefetch_related(
                'media',
                'variants',
                'product_categories__category',
            )
            .order_by('-created_at')[:18]
        )

        preview_products = []
        product_count_by_category = {}
        product_count_by_parent = {}

        for product in products:
            images = [m.url for m in product.media.all() if m.media_type == 'image']
            variants = [v for v in product.variants.all() if v.status == 'active']
            prices = [v.price for v in variants]
            currency = variants[0].currency if variants else 'UZS'
            product_categories = []
            if product.primary_category:
                product_categories.append(product.primary_category)
            product_categories.extend(
                pc.category for pc in product.product_categories.all()
                if pc.category and pc.category.is_active
            )
            unique_categories = list({category.id: category for category in product_categories}.values())
            parent_ids = {
                category.parent_id or category.id
                for category in unique_categories
            }
            for category in unique_categories:
                product_count_by_category[category.id] = product_count_by_category.get(category.id, 0) + 1
            for parent_id in parent_ids:
                product_count_by_parent[parent_id] = product_count_by_parent.get(parent_id, 0) + 1

            item = {
                'object': product,
                'image': images[0] if images else '',
                'price': min(prices) if prices else None,
                'currency': currency,
                'category_ids': ' '.join(f'cat-{category.id}' for category in unique_categories),
                'parent_ids': ' '.join(f'parent-{parent_id}' for parent_id in parent_ids if parent_id),
            }
            preview_products.append(item)

        for category in pet_categories:
            category['product_count'] = product_count_by_parent.get(category['object'].id, 0)
            for child in category['children']:
                child['product_count'] = product_count_by_category.get(child['object'].id, 0)

        return render(request, 'dashboard/mobile_preview.html', {
            'active': 'mobile_preview',
            'stats': _dashboard_stats(),
            'categories': categories,
            'pet_categories': pet_categories,
            'preview_products': preview_products,
        })


# ─── Products ─────────────────────────────────────────────────────────────────

@staff_required
class ProductListView(View):
    def get(self, request):
        qs = Product.objects.select_related('brand', 'primary_category', 'product_type').annotate(
            variant_count=Count('variants')
        )
        q = request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(brand__name__icontains=q) | Q(slug__icontains=q))

        status_f = request.GET.get('status', '')
        if status_f:
            qs = qs.filter(status=status_f)

        brand_f = request.GET.get('brand', '')
        if brand_f:
            qs = qs.filter(brand_id=brand_f)

        return render(request, 'dashboard/products/list.html', {
            'products': qs.order_by('-created_at'),
            'brands':   Brand.objects.filter(is_active=True),
            'q':        q,
            'status_f': status_f,
            'brand_f':  brand_f,
        })


@staff_required
class ProductCreateView(View):
    tpl = 'dashboard/products/form.html'

    def get(self, request):
        return render(request, self.tpl, {
            'form':            ProductForm(),
            'variant_formset': VariantFormSet(),
            'media_formset':   MediaFormSet(),
            'title':           "Yangi mahsulot qo'shish",
            'is_create':       True,
        })

    def post(self, request):
        form = ProductForm(request.POST)
        vfs  = VariantFormSet(request.POST)
        mfs  = MediaFormSet(request.POST)

        if form.is_valid() and vfs.is_valid() and mfs.is_valid():
            product = form.save()
            vfs.instance = product; vfs.save()
            mfs.instance = product; mfs.save()
            messages.success(request, f'"{product.name}" muvaffaqiyatli qo\'shildi.')
            return redirect('dashboard:product-edit', pk=product.pk)

        return render(request, self.tpl, {
            'form':            form,
            'variant_formset': vfs,
            'media_formset':   mfs,
            'title':           "Yangi mahsulot qo'shish",
            'is_create':       True,
        })


@staff_required
class ProductEditView(View):
    tpl = 'dashboard/products/form.html'

    def _get(self, pk):
        return get_object_or_404(
            Product.objects.select_related('product_type', 'brand'),
            pk=pk,
        )

    def get(self, request, pk):
        product = self._get(pk)
        return render(request, self.tpl, {
            'form':            ProductForm(instance=product),
            'variant_formset': VariantFormSet(instance=product),
            'media_formset':   MediaFormSet(instance=product),
            'product':         product,
            'title':           f'{product.name} — tahrirlash',
            'is_create':       False,
        })

    def post(self, request, pk):
        product = self._get(pk)
        form = ProductForm(request.POST, instance=product)
        vfs  = VariantFormSet(request.POST, instance=product)
        mfs  = MediaFormSet(request.POST, instance=product)

        if form.is_valid() and vfs.is_valid() and mfs.is_valid():
            product = form.save()
            vfs.save()
            mfs.save()
            messages.success(request, "O'zgarishlar saqlandi.")
            return redirect('dashboard:product-edit', pk=product.pk)

        return render(request, self.tpl, {
            'form':            form,
            'variant_formset': vfs,
            'media_formset':   mfs,
            'product':         product,
            'title':           f'{product.name} — tahrirlash',
            'is_create':       False,
        })


@staff_required
class ProductDeleteView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" o\'chirildi.')
        return redirect('dashboard:product-list')


# ─── Categories ───────────────────────────────────────────────────────────────

@staff_required
class CategoryListView(View):
    def get(self, request):
        cats = Category.objects.select_related('parent').annotate(
            child_count=Count('children'),
            product_count=Count('product_categories'),
        ).order_by('parent__name', 'sort_order', 'name')
        return render(request, 'dashboard/categories/list.html', {'categories': cats})


@staff_required
class CategoryFormView(View):
    tpl = 'dashboard/categories/form.html'

    def _instance(self, pk):
        return get_object_or_404(Category, pk=pk) if pk else None

    def get(self, request, pk=None):
        instance = self._instance(pk)
        return render(request, self.tpl, {'form': CategoryForm(instance=instance), 'instance': instance})

    def post(self, request, pk=None):
        instance = self._instance(pk)
        form = CategoryForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'"{obj.name}" saqlandi.')
            return redirect('dashboard:category-list')
        return render(request, self.tpl, {'form': form, 'instance': instance})


@staff_required
class CategoryDeleteView(View):
    def post(self, request, pk):
        obj = get_object_or_404(Category, pk=pk)
        name = obj.name
        obj.delete()
        messages.success(request, f'"{name}" o\'chirildi.')
        return redirect('dashboard:category-list')


# ─── Brands ───────────────────────────────────────────────────────────────────

@staff_required
class BrandListView(View):
    def get(self, request):
        brands = Brand.objects.annotate(product_count=Count('products')).order_by('name')
        return render(request, 'dashboard/brands/list.html', {'brands': brands})


@staff_required
class BrandFormView(View):
    tpl = 'dashboard/brands/form.html'

    def _instance(self, pk):
        return get_object_or_404(Brand, pk=pk) if pk else None

    def get(self, request, pk=None):
        instance = self._instance(pk)
        return render(request, self.tpl, {'form': BrandForm(instance=instance), 'instance': instance})

    def post(self, request, pk=None):
        instance = self._instance(pk)
        form = BrandForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'"{obj.name}" saqlandi.')
            return redirect('dashboard:brand-list')
        return render(request, self.tpl, {'form': form, 'instance': instance})


@staff_required
class BrandDeleteView(View):
    def post(self, request, pk):
        obj = get_object_or_404(Brand, pk=pk)
        name = obj.name
        obj.delete()
        messages.success(request, f'"{name}" o\'chirildi.')
        return redirect('dashboard:brand-list')


# ─── Product Types & Attributes ───────────────────────────────────────────────

@staff_required
class ProductTypeListView(View):
    def get(self, request):
        pts = ProductType.objects.prefetch_related('attributes').annotate(
            product_count=Count('products'),
            attr_count=Count('attributes'),
        )
        return render(request, 'dashboard/product_types/list.html', {'product_types': pts})


@staff_required
class ProductTypeFormView(View):
    tpl = 'dashboard/product_types/form.html'

    def _instance(self, pk):
        return get_object_or_404(ProductType, pk=pk) if pk else None

    def get(self, request, pk=None):
        instance = self._instance(pk)
        attrs = instance.attributes.prefetch_related('options').order_by('sort_order', 'name') if instance else []
        return render(request, self.tpl, {
            'form':      ProductTypeForm(instance=instance),
            'instance':  instance,
            'attrs':     attrs,
            'attr_form': AttributeDefinitionForm(),
            'opt_form':  AttributeOptionForm(),
        })

    def post(self, request, pk=None):
        instance = self._instance(pk)
        form = ProductTypeForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'"{obj.name}" saqlandi.')
            return redirect('dashboard:product-type-edit', pk=obj.pk)
        attrs = instance.attributes.all() if instance else []
        return render(request, self.tpl, {
            'form':      form,
            'instance':  instance,
            'attrs':     attrs,
            'attr_form': AttributeDefinitionForm(),
            'opt_form':  AttributeOptionForm(),
        })


@staff_required
class AttributeCreateView(View):
    def post(self, request, pt_pk):
        pt   = get_object_or_404(ProductType, pk=pt_pk)
        form = AttributeDefinitionForm(request.POST)
        if form.is_valid():
            attr = form.save(commit=False)
            attr.product_type = pt
            attr.save()
            messages.success(request, f'"{attr.name}" xususiyati qo\'shildi.')
        else:
            messages.error(request, 'Xususiyat qo\'shishda xato. Maydonlarni tekshiring.')
        return redirect('dashboard:product-type-edit', pk=pt_pk)


@staff_required
class AttributeDeleteView(View):
    def post(self, request, pk):
        attr = get_object_or_404(AttributeDefinition, pk=pk)
        pt_pk = attr.product_type_id
        attr.delete()
        messages.success(request, 'Xususiyat o\'chirildi.')
        return redirect('dashboard:product-type-edit', pk=pt_pk)


@staff_required
class AttributeOptionCreateView(View):
    def post(self, request, attr_pk):
        attr = get_object_or_404(AttributeDefinition, pk=attr_pk)
        form = AttributeOptionForm(request.POST)
        if form.is_valid():
            opt = form.save(commit=False)
            opt.attribute = attr
            opt.save()
            messages.success(request, f'"{opt.label}" qo\'shildi.')
        return redirect('dashboard:product-type-edit', pk=attr.product_type_id)


@staff_required
class AttributeOptionDeleteView(View):
    def post(self, request, pk):
        opt = get_object_or_404(AttributeOption, pk=pk)
        pt_pk = opt.attribute.product_type_id
        opt.delete()
        messages.success(request, 'Variant o\'chirildi.')
        return redirect('dashboard:product-type-edit', pk=pt_pk)
