from django.contrib import admin
from .models import Property, Reservation, PropertyImages
from django_summernote.admin import SummernoteModelAdmin


class PropertyImagesInline(admin.TabularInline):
    model = PropertyImages
    extra = 1  # Allows adding an extra image directly in the property admin page


@admin.register(Property)
class PropertyAdmin(SummernoteModelAdmin):  # Extending from SummernoteModelAdmin
    list_display = (
        "title",
        "price_per_night",
        "country",
        "city",
        "category",
        "landlord",
        "created_at",
    )
    list_filter = ("country","city", "category", "landlord")
    search_fields = ("title", "description", "country", "city", "category")
    inlines = [
        PropertyImagesInline
    ]  # Display property images inline on the property admin page
    ordering = ("-created_at",)
    list_per_page = 20  # Limit the number of items displayed per page
    summernote_fields = ("description",)  # Apply Summernote to the description field


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "property",
        "start_date",
        "end_date",
        "guests",
        "total_price",
        "created_by",
        "created_at",
    )
    list_filter = ("start_date", "end_date", "created_by", "property")
    search_fields = ("property__title", "created_by__email")
    ordering = ("-created_at",)
    date_hierarchy = "start_date"  # Adds a date drill-down feature
    list_per_page = 20


@admin.register(PropertyImages)
class PropertyImagesAdmin(admin.ModelAdmin):
    list_display = ("property", "image_url")
    search_fields = ("property__title",)
    list_filter = ("property",)
