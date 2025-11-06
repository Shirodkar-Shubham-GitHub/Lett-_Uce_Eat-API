from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='access-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('register/', RegisterAPI.as_view(), name='user-register')
]

urlpatterns += [
    path("auth/google/", GoogleAuthView.as_view(), name="google_auth"),
]

# urlpatterns += [
#     path('profile/', ProfileListAPI.as_view(), name='profile-detail'),
#     path('profile/create/', ProfileCreateAPI.as_view(), name='profile-create'),
#     path('profile/update/<int:pk>/', ProfileUpdateAPI.as_view(), name='profile-update'),
#     path('profile/delete/<int:pk>/', ProfileDeleteAPI.as_view(), name='profile-delete'),
# ]

urlpatterns += [
    # path('add-to-cart/', AddToCartAPI.as_view(), name='add_to_cart'),
    # path('remove-from-cart/<int:cart_item_id>/', DeleteCartItemAPI.as_view(), name='remove_from_cart'),
    path('hero_page/', HeroPageListAPI.as_view(), name='hero-page-detail'),
    path('menu_card/', MenuCardListAPI.as_view(), name='menu-card-detail'),
    path('dish_details/<slug:slug>/add_to_cart/', DishDetailsCreateAPI.as_view(), name='menu-item-create'),
    path('cart/', CartListAPI.as_view(), name='cart_items-detail'),
    path('cart/delete/<slug:slug>/', CartItemDeleteAPI.as_view(), name='cart-items-delete'),
    path('order/create/', CreateOrderAPI.as_view(), name='order-create'),
    path('order/confirm/', ConfirmOrderPaymentAPI.as_view(), name='order-confirm'),
    # path('cart/', ActiveOrdersListAPI.as_view(), name='active-order-cart'),
    # path('add_to_cart/', CartItemCreateAPI.as_view(), name='add-to-cart'),
    # path('order_details/', OrderDetailsListAPI.as_view(), name='order-details'),
    # path('order_post_details/', OrderPostDetailsListAPI.as_view(), name='order-post-details'),
]

urlpatterns += [
    path('menu_item/', MenuItemListAPI.as_view(), name='menu_item-detail'),
    path('menu_item/create/', MenuItemCreateAPI.as_view(), name='menu_item-create'),
    path('menu_item/update/<int:pk>/', MenuItemUpdateAPI.as_view(), name='menu_item-update'),
    path('menu_item/delete/<int:pk>/', MenuItemDeleteAPI.as_view(), name='menu_item-delete'),
]

urlpatterns += [
    path('order/', ActiveOrderListAPI.as_view(), name='order-detail'),
    path('past_order/', PastOrderListAPI.as_view(), name='past-order-detail'),
#     path('order/update/<int:pk>/', OrderUpdateAPI.as_view(), name='order-update'),
#     path('order/delete/<int:pk>/', OrderDeleteAPI.as_view(), name='order-delete'),
]

urlpatterns += [
    path('contact/', ContactListAPI.as_view(), name='contact-detail'),
    path('contact/create/', ContactCreateAPI.as_view(), name='contact-create'),
    path('contact/update/<int:pk>/', ContactUpdateAPI.as_view(), name='contact-update'),
    path('contact/delete/<int:pk>/', ContactDeleteAPI.as_view(), name='contact-delete'),
]
