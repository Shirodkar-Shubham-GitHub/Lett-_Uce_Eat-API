from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='access-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('register/', RegisterAPI.as_view(), name='user-register')
]

urlpatterns += [
    path('profile/', ProfileListAPI.as_view(), name='profile-detail'),
    path('profile/create/', ProfileCreateAPI.as_view(), name='profile-create'),
    path('profile/update/<int:pk>/', ProfileUpdateAPI.as_view(), name='profile-update'),
    path('profile/delete/<int:pk>/', ProfileDeleteAPI.as_view(), name='profile-delete'),
]

urlpatterns += [
    path('hero_page/', HeroPageListAPI.as_view(), name='hero-page-detail'),
    path('cart/', ActiveOrdersListAPI.as_view(), name='active-order-cart'),
    path('add_to_cart/', CartItemCreateAPI.as_view(), name='add-to-cart'),
    path('order_details/', OrderDetailsListAPI.as_view(), name='order-details'),
    path('order_post_details/', OrderPostDetailsListAPI.as_view(), name='order-post-details'),
]

urlpatterns += [
    path('menu_item/', MenuItemListAPI.as_view(), name='menu_item-detail'),
    path('menu_item/create/', MenuItemCreateAPI.as_view(), name='menu_item-create'),
    path('menu_item/update/<int:pk>/', MenuItemUpdateAPI.as_view(), name='menu_item-update'),
    path('menu_item/delete/<int:pk>/', MenuItemDeleteAPI.as_view(), name='menu_item-delete'),
]

urlpatterns += [
    path('order/', OrderListAPI.as_view(), name='order-detail'),
    path('order/create/', OrderCreateAPI.as_view(), name='order-create'),
    path('order/update/<int:pk>/', OrderUpdateAPI.as_view(), name='order-update'),
    path('order/delete/<int:pk>/', OrderDeleteAPI.as_view(), name='order-delete'),
]

urlpatterns += [
    path('order_item/', OrderItemListAPI.as_view(), name='order_item-detail'),
    path('order_item/create/', OrderItemCreateAPI.as_view(), name='order_item-create'),
    path('order_item/update/<int:pk>/', OrderItemUpdateAPI.as_view(), name='order_item-update'),
    path('order_item/delete/<int:pk>/', OrderItemDeleteAPI.as_view(), name='order_item-delete'),
]

urlpatterns += [
    path('delivery_address/', DeliveryAddressListAPI.as_view(), name='delivery_address-detail'),
    path('delivery_address/create/', DeliveryAddressCreateAPI.as_view(), name='delivery_address-create'),
    path('delivery_address/update/<int:pk>/', DeliveryAddressUpdateAPI.as_view(), name='delivery_address-update'),
    path('delivery_address/delete/<int:pk>/', DeliveryAddressDeleteAPI.as_view(), name='delivery_address-delete'),
]

urlpatterns += [
    path('contact/', ContactListAPI.as_view(), name='contact-detail'),
    path('contact/create/', ContactCreateAPI.as_view(), name='contact-create'),
    path('contact/update/<int:pk>/', ContactUpdateAPI.as_view(), name='contact-update'),
    path('contact/delete/<int:pk>/', ContactDeleteAPI.as_view(), name='contact-delete'),
]
