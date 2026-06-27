from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("watches/", views.watch_list, name="watch_list"),
    path("watches/<slug:slug>/", views.watch_detail, name="watch_detail"),
    path("watches/<slug:slug>/order/", views.place_order, name="place_order"),
    path("order/<int:order_id>/success/", views.order_success, name="order_success"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<slug:slug>/", views.category_detail, name="category_detail"),
    path("about/", views.about, name="about"),
]
