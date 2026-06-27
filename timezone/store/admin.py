from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Watch, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "watch_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def watch_count(self, obj):
        return obj.watches.count()
    watch_count.short_description = "Watches"


@admin.register(Watch)
class WatchAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "brand",
        "model",
        "title",
        "category",
        "price",
        "stock",
        "gender",
        "is_featured",
        "is_new_arrival",
        "created_at",
    )
    list_filter = ("category", "gender", "is_featured", "is_new_arrival", "movement")
    search_fields = ("brand", "model", "title", "description")
    list_editable = ("price", "stock", "is_featured", "is_new_arrival")
    prepopulated_fields = {"slug": ("brand", "model", "title")}
    readonly_fields = ("image_large_preview", "created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("category", "brand", "model", "title", "slug", "description")
        }),
        ("Pricing & Stock", {
            "fields": ("price", "stock")
        }),
        ("Specifications", {
            "fields": ("movement", "case_material", "strap_material", "water_resistance", "gender")
        }),
        ("Image", {
            "fields": ("image", "image_large_preview")
        }),
        ("Visibility", {
            "fields": ("is_featured", "is_new_arrival")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:45px;height:45px;object-fit:cover;'
                'border-radius:6px;" />',
                obj.image.url,
            )
        return "—"
    image_preview.short_description = "Image"

    def image_large_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:250px;border-radius:8px;" />',
                obj.image.url,
            )
        return "No image uploaded yet."
    image_large_preview.short_description = "Preview"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "watch",
        "quantity",
        "total_price",
        "status",
        "phone",
        "email",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "phone", "email", "watch__brand", "watch__model")
    list_editable = ("status",)
    readonly_fields = ("total_price", "created_at")
    date_hierarchy = "created_at"
    fieldsets = (
        ("Customer Information", {
            "fields": ("user", "customer_name", "phone", "email", "address")
        }),
        ("Order Details", {
            "fields": ("watch", "quantity", "total_price", "note", "status")
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )

    actions = ["mark_confirmed", "mark_cancelled"]

    def mark_confirmed(self, request, queryset):
        queryset.update(status=Order.STATUS_CONFIRMED)
    mark_confirmed.short_description = "Mark selected orders as Confirmed"

    def mark_cancelled(self, request, queryset):
        queryset.update(status=Order.STATUS_CANCELLED)
    mark_cancelled.short_description = "Mark selected orders as Cancelled"
