# Pet Market Backend Blueprint

Bu hujjat jonivorlar uchun ovqat, kiyim-kechak, uycha, aksessuar, dori/vitamin va boshqa mahsulotlar sotiladigan katta market backendini kengayuvchan qilish uchun yozildi. Maqsad: kategoriya, mahsulot, variant, xususiyat, filter, inventar, buyurtma va kontent qismlari keyinchalik qayta buzilmasdan kengayadigan universal modelga ega bo'lish.

## Research asoslari

Quyidagi ecommerce platformalari va search amaliyotlaridan g'oya olindi:

- Shopify metafields: standart `Product`, `Customer`, `Order` kabi modellarga turli maxsus maydonlarni qo'shish uchun type validation, schema definition, admin integration va query filtering ishlatiladi. Manba: https://shopify.dev/docs/apps/build/metafields
- Shopify product variant: variant alohida narx, barcode, media, inventory item, inventory policy va quantity bilan yuradi. Manba: https://shopify.dev/docs/api/admin-graphql/latest/objects/ProductVariant
- Algolia facets: filter/facetlarni tartiblash, yashirish va qiymatlarini alohida boshqarish kerak; custom UI bo'lsa search response ichidagi facet metadata frontend tomonidan to'g'ri talqin qilinadi. Manba: https://www.algolia.com/doc/guides/building-search-ui/ui-and-ux-patterns/facet-display/js
- commercetools product types: product type ichida attributelar schema sifatida beriladi; attribute product yoki variant darajasida bo'lishi, required bo'lishi, enum/boolean/number/date/text kabi typelarga ega bo'lishi mumkin. Manba: https://docs.commercetools.com/api/projects/productTypes

## Asosiy prinsiplar

- Category daraxt bo'lishi kerak: masalan `Itlar -> Ovqat -> Quruq ovqat`, `Mushuklar -> Gigiyena -> Qum`.
- Product va variant ajratiladi: `Royal Canin Mini Adult` product, `2kg`, `4kg`, `8kg` variant.
- Category-specific attribute schema bo'ladi: ovqatda `protein_percent`, kiyimda `size`, uycha/tashuvchida `dimensions`, dorida `age_group` va `prescription_required`.
- Filterlar hardcode qilinmaydi. Admin xususiyat yaratadi, kategoriya bilan bog'laydi, mahsulot yoki variant qiymat oladi.
- Search uchun transactional database va search index alohida qaraladi. DB canonical source, search index esa tez o'qish/filterlash uchun materialized view.
- Narx, stock, order va payment history hech qachon oddiy overwrite bilan yo'qolmasligi kerak.

## Domen modullari

1. Catalog
   - Category tree
   - Product type/schema
   - Product
   - Product variant
   - Brand
   - Collection yoki merchandising group
   - Media gallery
   - Attribute definitions va attribute values

2. Search and Filtering
   - Full-text search
   - Faceted filters
   - Category-aware filters
   - Sorting
   - Synonyms
   - Search analytics

3. Pricing and Promotions
   - Base price
   - Compare-at price
   - Discount/coupon
   - Campaign
   - Price history
   - Currency support

4. Inventory
   - SKU
   - Barcode
   - Warehouse/location
   - Stock movement
   - Reservation
   - Low-stock alert

5. Cart and Checkout
   - Cart
   - Cart item
   - Shipping address
   - Delivery method
   - Payment intent/transaction
   - Order placement

6. Order Management
   - Order
   - Order item snapshot
   - Status workflow
   - Payment status
   - Fulfillment/shipment
   - Refund/cancel
   - Return request

7. Users and Customer Experience
   - Customer profile
   - Pet profiles
   - Wishlist
   - Product reviews
   - Recently viewed products
   - Recommendations

8. Admin and Operations
   - Staff roles/permissions
   - Audit log
   - Import/export
   - Moderation
   - Webhooks/integrations

## Tavsiya qilingan data model

### Category

Maydonlar:

- `id`
- `parent_id`
- `name`
- `slug`
- `description`
- `image`
- `is_active`
- `sort_order`
- `seo_title`
- `seo_description`
- `created_at`
- `updated_at`

Texnik variantlar:

- Boshlanishiga `parent_id` adjacency list yetadi.
- Kategoriya daraxti chuqurlashsa `django-mptt` yoki materialized path (`path`, `depth`) ishlatish ma'qul.
- Category slug bitta parent ichida unique bo'lishi kerak.

### ProductType

Product type category ichidagi attribute schema uchun kerak. Masalan:

- `Pet Food`
- `Pet Clothing`
- `Pet House`
- `Carrier`
- `Medicine`
- `Toy`

Maydonlar:

- `id`
- `name`
- `slug`
- `description`
- `is_active`

### AttributeDefinition

Qo'lda qo'shiladigan universal xususiyatlar shu modelda turadi.

Maydonlar:

- `id`
- `product_type_id`
- `name`
- `code`
- `data_type`: `text`, `number`, `decimal`, `boolean`, `enum`, `multi_enum`, `date`, `dimension`, `weight`
- `unit`: `kg`, `g`, `cm`, `ml`, `%` va hokazo
- `is_required`
- `is_filterable`
- `is_searchable`
- `is_variant_level`
- `is_public`
- `sort_order`
- `validation_rules`: JSON
- `help_text`

Misollar:

- Food: `animal_type`, `breed_size`, `life_stage`, `flavor`, `weight`, `protein_percent`, `grain_free`
- Clothing: `animal_type`, `size`, `neck_girth`, `chest_girth`, `material`, `color`, `season`
- House: `animal_type`, `dimensions`, `material`, `indoor_outdoor`, `weight_capacity`
- Medicine/vitamin: `animal_type`, `life_stage`, `active_ingredient`, `dosage_form`, `prescription_required`

### AttributeOption

Enum va multi-enum qiymatlari uchun.

Maydonlar:

- `id`
- `attribute_id`
- `value`
- `label`
- `slug`
- `sort_order`
- `is_active`

### Product

Mahsulotning asosiy, variantlardan umumiy ma'lumotlari.

Maydonlar:

- `id`
- `product_type_id`
- `brand_id`
- `name`
- `slug`
- `description`
- `short_description`
- `status`: `draft`, `active`, `archived`
- `primary_category_id`
- `seo_title`
- `seo_description`
- `created_at`
- `updated_at`

Bog'lanishlar:

- Product ko'p categoryga ulanadi: `ProductCategory`
- Product ko'p mediaga ega: `ProductMedia`
- Product umumiy attributelarga ega: `ProductAttributeValue`

### ProductCategory

Mahsulot bitta primary categoryga ega bo'lishi mumkin, lekin ko'p categoryda ko'rinishi kerak.

Maydonlar:

- `product_id`
- `category_id`
- `is_primary`
- `sort_order`

### ProductVariant

Sotiladigan haqiqiy birlik. Narx, SKU va stock variant darajasida yuradi.

Maydonlar:

- `id`
- `product_id`
- `sku`
- `barcode`
- `name`
- `slug`
- `price`
- `compare_at_price`
- `cost_price`
- `currency`
- `weight`
- `status`
- `is_default`
- `created_at`
- `updated_at`

Misol:

- Product: `Royal Canin Mini Adult`
- Variantlar: `2kg`, `4kg`, `8kg`

### ProductAttributeValue / VariantAttributeValue

Qiymatlar type-safe saqlanishi kerak. Ikki yondashuv bor:

1. EAV model:
   - `attribute_id`
   - `product_id` yoki `variant_id`
   - `value_text`
   - `value_number`
   - `value_decimal`
   - `value_boolean`
   - `value_date`
   - `value_json`
   - `option_id`

2. JSONB model:
   - `product.attributes = JSONB`
   - `variant.attributes = JSONB`

Django/PostgreSQL uchun amaliy tavsiya:

- Canonical schema uchun `AttributeDefinition`.
- Tez ishlab chiqish uchun product/variant qiymatlarini JSONFieldda saqlash mumkin.
- Filter tezligi muhim bo'lganda EAV yoki denormalized search index qo'shiladi.
- PostgreSQL JSONB GIN index ishlatiladi, lekin enum/number range filterlar ko'payganda alohida indexlangan jadval yaxshi ishlaydi.

### Brand

Maydonlar:

- `id`
- `name`
- `slug`
- `logo`
- `description`
- `country`
- `is_active`

### Media

Maydonlar:

- `id`
- `product_id`
- `variant_id`
- `type`: `image`, `video`
- `url`
- `alt_text`
- `sort_order`
- `is_primary`

### Inventory

Katta marketda `Product.stock` yetarli emas. Stock variant va location darajasida bo'lishi kerak.

Model:

- `Warehouse`: ombor yoki do'kon
- `InventoryItem`: variant bilan 1:1 yoki 1:N
- `StockLevel`: variant + warehouse bo'yicha quantity
- `StockMovement`: kirim/chiqim/reservation/correction tarixi

Maydonlar:

- `variant_id`
- `warehouse_id`
- `quantity_on_hand`
- `quantity_reserved`
- `quantity_available`
- `low_stock_threshold`

### Cart

Maydonlar:

- `id`
- `user_id`
- `session_key`
- `status`
- `currency`
- `created_at`
- `updated_at`

CartItem:

- `cart_id`
- `variant_id`
- `quantity`
- `unit_price_snapshot`

### Order

Buyurtma qo'yilganda product/variant ma'lumotlari snapshot qilinadi. Keyin mahsulot nomi yoki narxi o'zgarsa ham eski order buzilmaydi.

Order:

- `id`
- `order_number`
- `user_id`
- `status`
- `payment_status`
- `fulfillment_status`
- `subtotal`
- `discount_total`
- `shipping_total`
- `tax_total`
- `grand_total`
- `currency`
- `customer_note`
- `created_at`

OrderItem:

- `order_id`
- `variant_id`
- `sku_snapshot`
- `product_name_snapshot`
- `variant_name_snapshot`
- `attributes_snapshot`
- `unit_price`
- `quantity`
- `total`

## Filter/search talablari

### Filter turlari

- Category tree filter
- Price range
- Brand
- Animal type: dog, cat, bird, fish, rabbit va boshqalar
- Life stage: puppy/kitten/adult/senior
- Breed size: small/medium/large
- Food type: dry/wet/treat/vitamin
- Weight/volume range
- Flavor
- Material
- Size
- Color
- In stock only
- Rating
- Discounted only
- Prescription required

### Category-aware filter

Har category har xil filter ko'rsatadi:

- `Itlar -> Ovqat`: brand, age, breed size, flavor, weight, food type
- `Mushuklar -> Qum`: brand, scent, clumping, weight
- `Kiyim`: size, color, material, season
- `Uycha`: dimensions, material, indoor/outdoor, animal size

### Search index document

Search enginega yuboriladigan document taxminan shunday:

```json
{
  "product_id": 1,
  "variant_ids": [10, 11],
  "name": "Royal Canin Mini Adult",
  "brand": "Royal Canin",
  "categories": ["Itlar", "Ovqat", "Quruq ovqat"],
  "category_ids": [1, 2, 3],
  "price_min": 120000,
  "price_max": 430000,
  "in_stock": true,
  "rating": 4.8,
  "attributes": {
    "animal_type": ["dog"],
    "life_stage": ["adult"],
    "breed_size": ["small"],
    "food_type": ["dry"],
    "weight": [2, 4, 8]
  }
}
```

### Search engine tanlovi

- Boshlanishiga PostgreSQL full-text search + indexlangan filterlar yetadi.
- Katalog kattalashsa Meilisearch, Typesense, Elasticsearch/OpenSearch yoki Algolia kerak bo'ladi.
- Search indexni background job orqali yangilash kerak.

## Pet-marketga xos qo'shimcha imkoniyatlar

- Pet profile: foydalanuvchi it/mushuk turi, yoshi, vazni, allergiyasi, breedini kiritadi.
- Personalized recommendation: pet profilega mos ovqat, vitamin, kiyim size.
- Subscription/repeat order: oylik ovqat yoki qum avtomatik buyurtma.
- Feeding calculator: vazn/yosh/faollikka qarab kunlik ovqat miqdori.
- Compatibility warning: masalan, mahsulot faqat mushuklar uchun yoki faqat senior dog uchun.
- Prescription flag: ayrim dori yoki veterinary diet mahsulotlari uchun retsept/admin tasdiq.
- Bundle/kits: `puppy starter kit`, `cat hygiene kit`.
- Size guide: kiyim va uycha uchun o'lcham jadvali.
- Expiration date tracking: ovqat, dori, vitamin uchun partiya va yaroqlilik muddati.
- Batch/lot tracking: recall bo'lsa qaysi orderlarga ta'sir qilganini topish.
- Review moderation: rasmli review, rating, admin approval.
- Q&A: mahsulot bo'yicha savol-javob.
- Delivery constraints: og'ir mahsulotlar, sovuq zanjir talab qiladigan mahsulotlar, hudud bo'yicha shipping.

## API endpointlar

Public catalog:

- `GET /api/categories/`
- `GET /api/categories/tree/`
- `GET /api/categories/{slug}/`
- `GET /api/products/`
- `GET /api/products/{slug}/`
- `GET /api/products/{id}/variants/`
- `GET /api/filters/?category={slug}`
- `GET /api/search/?q=...`

Cart/order:

- `GET /api/cart/`
- `POST /api/cart/items/`
- `PATCH /api/cart/items/{id}/`
- `DELETE /api/cart/items/{id}/`
- `POST /api/checkout/`
- `GET /api/orders/`
- `GET /api/orders/{id}/`
- `POST /api/orders/{id}/cancel/`

Customer:

- `GET /api/profile/`
- `GET /api/pets/`
- `POST /api/pets/`
- `GET /api/wishlist/`
- `POST /api/wishlist/items/`
- `POST /api/products/{id}/reviews/`

Admin:

- `POST /api/admin/categories/`
- `POST /api/admin/product-types/`
- `POST /api/admin/attributes/`
- `POST /api/admin/products/`
- `POST /api/admin/variants/`
- `POST /api/admin/inventory/movements/`
- `POST /api/admin/import/products/`

## Admin panel talablari

- Category daraxtini drag/drop tartiblash.
- Product type yaratish.
- Product typega attribute qo'shish.
- Attribute uchun enum optionlar qo'shish.
- Attribute filterda chiqadimi, searchda qatnashadimi belgilash.
- Product/variant yaratishda category va product typega qarab dinamik forma.
- Bulk import/export: CSV/XLSX.
- Media upload.
- Price va stock bulk update.
- Order status boshqaruvi.
- Audit log: kim nima o'zgartirdi.

## Status workflow

Product status:

- `draft`
- `active`
- `out_of_stock`
- `archived`

Order status:

- `pending`
- `confirmed`
- `processing`
- `shipped`
- `delivered`
- `cancelled`
- `refunded`

Payment status:

- `unpaid`
- `authorized`
- `paid`
- `partially_refunded`
- `refunded`
- `failed`

Fulfillment status:

- `unfulfilled`
- `partially_fulfilled`
- `fulfilled`
- `returned`

## Texnik arxitektura tavsiyasi

Boshlang'ich stack:

- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- S3-compatible object storage

Keyingi bosqich:

- Meilisearch/Typesense yoki Elasticsearch/OpenSearch
- Payment provider integration
- SMS/email/push notification service
- Background import pipeline
- Analytics events

Apps bo'yicha bo'lish:

- `catalog`: category, product, variant, attributes, media, brand
- `inventory`: warehouse, stock, stock movement
- `pricing`: price list, discount, coupon
- `cart`: cart, cart item
- `orders`: order, order item, fulfillment, refund
- `customers`: profile, pet profile, address, wishlist
- `reviews`: review, rating, Q&A
- `search`: indexing, search API, filters
- `payments`: payment intent, transaction, webhook
- `shipping`: delivery method, zone, rate

## Django model yo'nalishi

Hozirgi `products.models.Product` juda sodda. Uni to'g'ridan-to'g'ri kattalashtirish o'rniga catalog domenini qayta ajratish kerak:

- `Category`
- `ProductType`
- `AttributeDefinition`
- `AttributeOption`
- `Brand`
- `Product`
- `ProductVariant`
- `ProductCategory`
- `ProductMedia`
- `ProductAttributeValue`
- `VariantAttributeValue`

Minimal birinchi iteratsiya:

1. Category tree
2. ProductType
3. AttributeDefinition + AttributeOption
4. Product + ProductVariant
5. ProductCategory
6. JSONField asosida product/variant attributes
7. Filter endpoint

Ikkinchi iteratsiya:

1. PostgreSQLga o'tish
2. DRF API
3. Search index
4. Inventory module
5. Cart/order module

Uchinchi iteratsiya:

1. Payment
2. Shipping
3. Reviews/wishlist
4. Pet profiles
5. Subscription/repeat orders
6. Admin import/export

## Index va performance

DB indexlar:

- `Category(parent_id, sort_order)`
- `Category(slug)`
- `Product(slug)`
- `Product(status)`
- `ProductVariant(product_id)`
- `ProductVariant(sku)`
- `ProductVariant(price)`
- `ProductCategory(category_id, product_id)`
- `AttributeDefinition(product_type_id, code)`
- JSONB attributes uchun GIN index

Cache:

- Category tree cache
- Filter metadata cache
- Product detail cache
- Search result qisqa TTL cache

Background jobs:

- Search index sync
- Image resize/optimization
- Bulk import validation
- Low-stock notification
- Abandoned cart reminder
- Review moderation notification

## Security va compliance

- Admin role-based permission.
- Payment ma'lumotlarini o'zimiz saqlamaslik, provider token/transaction id saqlash.
- Webhook signature verification.
- Rate limiting.
- Audit log.
- User PII encryption yoki kamida qat'iy access control.
- Soft delete kerak bo'lgan joylarda `is_deleted/deleted_at`.

## Qarorlar

- `Product.stock` o'rniga `ProductVariant + Inventory` ishlatiladi.
- Xususiyat/filterlar admin orqali dinamik yaratiladi.
- Product type attribute schema markaziy o'rinda bo'ladi.
- Order itemlar snapshot saqlaydi.
- Search/filter uchun alohida indexga tayyor model qilinadi.
- Pet profile va subscription keyingi bosqichga qoldirilsa ham schema ularga yo'l berishi kerak.

## Ochiladigan savollar

- Loyiha bitta sotuvchimi yoki multi-vendor marketplace bo'ladimi?
- Yetkazib berish faqat bitta shahar ichidami yoki regionlar bo'yicha ham bormi?
- Online payment birinchi versiyada kerakmi?
- Product import qaysi formatdan bo'ladi: CSV, Excel, 1C, vendor API?
- Ombor bitta bo'ladimi yoki ko'p location kerakmi?
- Dori/veterinary diet mahsulotlarida retsept yoki veterinar tasdig'i kerakmi?
- Til va valuta nechta bo'ladi?

