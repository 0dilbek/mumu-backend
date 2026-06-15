from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),

    # Products
    path('products/',                      views.ProductListView.as_view(),   name='product-list'),
    path('products/create/',               views.ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/edit/',        views.ProductEditView.as_view(),   name='product-edit'),
    path('products/<int:pk>/delete/',      views.ProductDeleteView.as_view(), name='product-delete'),

    # Categories
    path('categories/',                    views.CategoryListView.as_view(),  name='category-list'),
    path('categories/create/',             views.CategoryFormView.as_view(),  name='category-create'),
    path('categories/<int:pk>/edit/',      views.CategoryFormView.as_view(),  name='category-edit'),
    path('categories/<int:pk>/delete/',    views.CategoryDeleteView.as_view(),name='category-delete'),

    # Brands
    path('brands/',                        views.BrandListView.as_view(),     name='brand-list'),
    path('brands/create/',                 views.BrandFormView.as_view(),     name='brand-create'),
    path('brands/<int:pk>/edit/',          views.BrandFormView.as_view(),     name='brand-edit'),
    path('brands/<int:pk>/delete/',        views.BrandDeleteView.as_view(),   name='brand-delete'),

    # Product types
    path('product-types/',                 views.ProductTypeListView.as_view(),  name='product-type-list'),
    path('product-types/create/',          views.ProductTypeFormView.as_view(),  name='product-type-create'),
    path('product-types/<int:pk>/edit/',   views.ProductTypeFormView.as_view(),  name='product-type-edit'),

    # Attributes
    path('product-types/<int:pt_pk>/attributes/create/', views.AttributeCreateView.as_view(),       name='attribute-create'),
    path('attributes/<int:pk>/delete/',                  views.AttributeDeleteView.as_view(),        name='attribute-delete'),
    path('attributes/<int:attr_pk>/options/create/',     views.AttributeOptionCreateView.as_view(),  name='attr-option-create'),
    path('attribute-options/<int:pk>/delete/',           views.AttributeOptionDeleteView.as_view(),  name='attr-option-delete'),
]
