from django.db.models import Q
from rest_framework.decorators import api_view

from common.permissions import require_staff
from common.responses import error, ok
from common.views import health_response
from products.models import Category, Inventory, Product
from products.serializers import CategorySerializer, InventorySerializer, PRODUCT_TYPE_CONFIG, ProductSerializer


@api_view(["GET"])
def health(request):
    return health_response("product_service")


def _product_queryset():
    return Product.objects.select_related(
        "category",
        "inventory",
        *[config["related_name"] for config in PRODUCT_TYPE_CONFIG.values()],
    ).prefetch_related("images", "attribute_values")


@api_view(["GET", "POST"])
def product_collection(request):
    if request.method == "GET":
        queryset = _product_queryset().order_by("-created_at")
        return ok(ProductSerializer(queryset, many=True).data)

    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    serializer = ProductSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    product = serializer.save()
    return ok(ProductSerializer(product).data, "Product created", status=201)


@api_view(["GET", "PATCH", "DELETE"])
def product_detail(request, product_id):
    try:
        product = _product_queryset().get(id=product_id)
    except Product.DoesNotExist:
        return error("PRODUCT_NOT_FOUND", "Product not found", status=404)

    if request.method == "GET":
        return ok(ProductSerializer(product).data)

    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    if request.method == "DELETE":
        product.delete()
        return ok({}, "Product deleted")

    serializer = ProductSerializer(product, data=request.data, partial=True)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    product = serializer.save()
    return ok(ProductSerializer(product).data, "Product updated")


@api_view(["GET"])
def product_search(request):
    queryset = _product_queryset().filter(status="ACTIVE")
    query = request.query_params.get("q")
    category = request.query_params.get("category")
    product_type = request.query_params.get("product_type")
    min_price = request.query_params.get("min_price")
    max_price = request.query_params.get("max_price")

    if query:
        queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__icontains=query))
    if category:
        queryset = queryset.filter(Q(category_id=category) | Q(category__slug=category))
    if product_type:
        config = PRODUCT_TYPE_CONFIG.get(product_type)
        if not config:
            return error("INVALID_PRODUCT_TYPE", "Unknown product type", status=400)
        queryset = queryset.filter(**{f"{config['related_name']}__isnull": False})
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)

    return ok(ProductSerializer(queryset.order_by("name"), many=True).data)


@api_view(["GET"])
def related_products(request, product_id):
    try:
        product = Product.objects.select_related("category").get(id=product_id)
    except Product.DoesNotExist:
        return error("PRODUCT_NOT_FOUND", "Product not found", status=404)

    product_type = ProductSerializer(product).data["type"]
    queryset = _product_queryset().filter(status="ACTIVE", category=product.category).exclude(id=product.id)
    config = PRODUCT_TYPE_CONFIG.get(product_type)
    if config:
        same_type = queryset.filter(**{f"{config['related_name']}__isnull": False})[:4]
        mixed_type = queryset.exclude(**{f"{config['related_name']}__isnull": False})[:4]
        queryset = list(same_type) + list(mixed_type)
    else:
        queryset = queryset[:8]
    return ok(ProductSerializer(queryset, many=True).data)


@api_view(["GET", "PATCH"])
def inventory_detail(request, product_id):
    try:
        inventory = Inventory.objects.select_related("product").get(product_id=product_id)
    except Inventory.DoesNotExist:
        return error("INVENTORY_NOT_FOUND", "Inventory not found", status=404)

    if request.method == "GET":
        return ok(InventorySerializer(inventory).data)

    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    serializer = InventorySerializer(inventory, data=request.data, partial=True)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    serializer.save()
    return ok(serializer.data, "Inventory updated")


@api_view(["GET", "POST"])
def category_collection(request):
    if request.method == "GET":
        return ok(CategorySerializer(Category.objects.all().order_by("name"), many=True).data)

    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    serializer = CategorySerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    category = serializer.save()
    return ok(CategorySerializer(category).data, "Category created", status=201)


@api_view(["PATCH", "DELETE"])
def category_detail(request, category_id):
    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return error("CATEGORY_NOT_FOUND", "Category not found", status=404)

    if request.method == "DELETE":
        category.delete()
        return ok({}, "Category deleted")

    serializer = CategorySerializer(category, data=request.data, partial=True)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    serializer.save()
    return ok(serializer.data, "Category updated")


@api_view(["GET"])
def ai_export(request):
    products = _product_queryset().filter(status="ACTIVE").order_by("id")
    data = []
    for product in products:
        inventory = getattr(product, "inventory", None)
        serialized = ProductSerializer(product).data
        data.append(
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": str(product.price),
                "category": product.category.name if product.category else None,
                "brand": product.brand,
                "stock": inventory.available_quantity if inventory else 0,
                "product_type": serialized["type"],
                "type_details": serialized["type_details"],
            }
        )
    return ok(data)


@api_view(["POST"])
def rebuild_embedding_placeholder(request, product_id):
    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    if not Product.objects.filter(id=product_id).exists():
        return error("PRODUCT_NOT_FOUND", "Product not found", status=404)
    return ok({"product_id": product_id, "status": "queued"}, "Embedding rebuild queued")
