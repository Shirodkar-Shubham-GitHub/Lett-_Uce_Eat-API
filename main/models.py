from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone

class TimeStampedSoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    OUT_FOR_DELIVERY = 'out_for_delivery', 'Out For Delivery'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'

PHONE_REGEX_VALIDATOR = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message="Phone number must be valid."
)


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    # phone_regex = RegexValidator(regex=r'^\+?\d{10,15}$', message="Phone number must be valid.")
    phone = models.CharField(max_length=16, unique=True, validators=[PHONE_REGEX_VALIDATOR], null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)

    # # Soft delete fields
    # is_deleted = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Users"
        db_table = "users"

    def __str__(self):
        return self.username


class Profile(TimeStampedSoftDeleteModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False, null=False, blank=False)

    # # Soft delete fields
    # is_deleted = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Profiles"
        db_table = "profiles"

    def __str__(self):
        return self.user.username
    
class MenuItem(TimeStampedSoftDeleteModel):
    name = models.CharField(max_length=150, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_items/', blank=False, null=False)

    # # Soft delete fields
    # is_deleted = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Menu items"
        db_table = "menuitems"

    def __str__(self):
        return self.name


class Order(TimeStampedSoftDeleteModel):

    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    # total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    # # Soft delete fields
    # is_deleted = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Orders"
        db_table = "orders"

    def __str__(self):
        return f"Order by {self.customer.username}"


class OrderItem(TimeStampedSoftDeleteModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False)

    # # Soft delete fields
    # is_deleted = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Order items"
        db_table = "orderitems"

    def get_total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"


class DeliveryAddress(TimeStampedSoftDeleteModel):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_address')
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)

    # # Soft delete fields
    # is_deleted = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Delivery addresses"
        db_table = "deliveryaddress"

    def __str__(self):
        return f"Address for Order #{self.order.id}"


class Contact(TimeStampedSoftDeleteModel):
    name = models.CharField(max_length=200, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    # phone_regex = RegexValidator(regex=r'^\+?\d{10,15}$', message="Phone number must be valid.")
    phone = models.CharField(max_length=16, unique=False, validators=[PHONE_REGEX_VALIDATOR], null=True, blank=True)
    message = models.TextField(null=False, blank=False)

    # # Soft delete fields
    # is_deleted = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Contacts"
        db_table = "contact"

    def __str__(self):
        return self.name
