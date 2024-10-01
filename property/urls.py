from django.urls import path

from . import api


urlpatterns = [
    path("", api.properties_list, name="api_properties_list"),
    path("create/", api.create_property, name="api_create_property"),
    path("<uuid:pk>/", api.properties_detail, name="api_properties_detail"),
    path("<uuid:pk>/book/", api.book_property, name="api_book_property"),
    path("<uuid:pk>/cancel/", api.cancel_reservation, name="cancel_reservation"),
    path(
        "<uuid:pk>/reservations/",
        api.property_reservations,
        name="api_property_reservations",
    ),
    path("<uuid:pk>/toggle_favorite/", api.toggle_favorite, name="api_toggle_favorite"),
    path("<uuid:property_id>/edit/", api.edit_property, name="edit_property"),
    path("<uuid:property_id>/delete/", api.delete_property, name="delete_property"),
]
