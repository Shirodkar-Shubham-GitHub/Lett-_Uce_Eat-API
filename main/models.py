from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.text import slugify

class TimeStampedSoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

class ApprovalStatus(models.TextChoices):
    APPROVED = 'approved', 'Approved'
    PENDING = 'pending', 'Pending'
    REJECTED = 'rejected', 'Rejected'

class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    OUT_FOR_DELIVERY = 'out_for_delivery', 'Out For Delivery'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'

class States(models.TextChoices):
    ALL = '', 'All'
    ANDHRA_PRADESH = "andhrapradesh", "Andhra Pradesh"
    ARUNACHAL_PRADESH = "arunachalpradesh", "Arunachal Pradesh"
    ASSAM = "assam", "Assam"
    BIHAR = "bihar", "Bihar"
    CHANDIGARH = "chandigarh", "Chandigarh"
    CHHATTISGARH = "chhattisgarh", "Chhattisgarh"
    DADRA_AND_NAGAR_HAVELI = "dadraandnagarhaveli", "Dadra and Nagar Haveli"
    DAMAN_AND_DIU = "damananddiu", "Daman and Diu"
    DELHI = "delhi", "Delhi"
    GOA = "goa", "Goa"
    GUJARAT = "gujarat", "Gujarat"
    HARYANA = "haryana", "Haryana"
    HIMACHAL_PRADESH = "himachalpradesh", "Himachal Pradesh"
    JAMMU_AND_KASHMIR = "jammuandkashmir", "Jammu and Kashmir"
    JHARKHAND = "jharkhand", "Jharkhand"
    KARNATAKA = "karnataka", "Karnataka"
    KERALA = "kerala", "Kerala"
    MADHYA_PRADESH = "madhyapradesh", "Madhya Pradesh"
    MAHARASHTRA = "maharashtra", "Maharashtra"
    MANIPUR = "manipur", "Manipur"
    MEGHALAYA = "meghalaya", "Meghalaya"
    MIZORAM = "mizoram", "Mizoram"
    NAGALAND = "nagaland", "Nagaland"
    ODISHA = "odisha", "Odisha"
    PUDUCHERRY = "puducherry", "Puducherry"
    PUNJAB = "punjab", "Punjab"
    RAJASTHAN = "rajasthan", "Rajasthan"
    SIKKIM = "sikkim", "Sikkim"
    TAMIL_NADU = "tamilnadu", "Tamil Nadu"
    TELANGANA = "telangana", "Telangana"
    TRIPURA = "tripura", "Tripura"
    UTTAR_PRADESH = "uttarpradesh", "Uttar Pradesh"
    UTTARAKHAND = "uttarakhand", "Uttarakhand"
    WEST_BENGAL = "westbengal", "West Bengal"

class Cuisines(models.TextChoices):
    ALL = '', 'All'
    ITALIAN = "italian", "Italian"
    CHINESE = "chinese", "Chinese"
    NORTH_INDIAN = "northindian", "North Indian"
    SOUTH_INDIAN = "southindian", "South Indian"
    MEXICAN = "mexican", "Mexican"
    THAI = "thai", "Thai"
    JAPANESE = "japanese", "Japanese"
    CONTINENTAL = "continental", "Continental"
    AMERICAN = "american", "American"    #    "american", "US"
    FRENCH = "french", "French"
    KOREAN = "korean", "Korean"
    VIETNAMESE = "vietnamese", "Vietnamese"
    BENGALI = "bengali", "Bengali"
    KERALA = "kerala", "Kerala"
    RAJASTHANI = "rajasthani", "Rajasthani"
    PUNJABI = "punjabi", "Punjabi"
    GUJARATI = "gujarati", "Gujarati"
    MAHARASHTRIAN = "maharashtrian", "Maharashtrian"

class DietType(models.TextChoices):
    ALL = '', 'All'
    VEG = "veg", "Veg"
    NON_VEG = "nonveg", "Non-Veg"
    VEGAN = "vegan", "Vegan"
    JAIN = "jain", "Jain"

PHONE_REGEX_VALIDATOR = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message="Phone number must be valid."
)


class CustomUser(AbstractUser, TimeStampedSoftDeleteModel):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=16, unique=True, validators=[PHONE_REGEX_VALIDATOR], null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, choices=States.choices, default=States.ALL, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    # user_verified = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)

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


class Badge(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Badges"

class MenuItem(TimeStampedSoftDeleteModel):
    image = models.ImageField(upload_to='menu_items/', blank=False, null=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False)
    is_available = models.BooleanField(default=True)
    cuisine = models.CharField(max_length=255, choices=Cuisines.choices, default=Cuisines.ALL)
    diet_type = models.CharField(max_length=255, choices=DietType.choices, default=DietType.ALL)
    badges = models.ManyToManyField(Badge, default=None, related_name='menu_items', blank=True)
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)
    #  rating

    def save(self, *args, **kwargs):
        if not self.slug:
            words = self.name.split()
            if len(words) <= 5:
                slug_base = self.name
            else:
                timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
                slug_base = "-".join(words[:5]) + "-" + timestamp
            slug = slugify(slug_base)
            model_class = self.__class__
            counter = 1
            while model_class.objects.filter(slug=slug).exists():
                slug = f"{slugify(slug_base)}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

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


class Cart(TimeStampedSoftDeleteModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='carts_user')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='carts_menu_item', null=True)
    quantity = models.PositiveIntegerField(default=1)
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)

    def total_price(self):
        return self.quantity * self.menu_item.price

    def __str__(self):
        return f"{self.menu_item.name} - {self.quantity} x {self.menu_item.price}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            words = self.menu_item.name.split()
            if len(words) <= 5:
                slug_base = self.menu_item.name
            else:
                timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
                slug_base = "-".join(words[:5]) + "-" + timestamp
            slug = slugify(slug_base)
            model_class = self.__class__
            counter = 1
            while model_class.objects.filter(slug=slug).exists():
                slug = f"{slugify(slug_base)}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Carts"
        db_table = "carts"


class Order(TimeStampedSoftDeleteModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders_user', null=True)
    dish = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='orders_dish', null=True)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=255, choices=OrderStatus.choices, default=OrderStatus.PENDING, null=True, blank=True)
    # is_ordered = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)

    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)

    def calculate_total_price(self):
        return self.quantity * self.dish.price

    def __str__(self):
        if self.dish:
            return f"Order {self.id} - {self.dish.name}"
        else:
            return f"Order {self.id} - No dish assigned"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            words = self.dish.name.split()
            if len(words) <= 5:
                slug_base = self.dish.name
            else:
                timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
                slug_base = "-".join(words[:5]) + "-" + timestamp + "order"
            slug = slugify(slug_base)
            model_class = self.__class__
            counter = 1
            while model_class.objects.filter(slug=slug).exists():
                slug = f"{slugify(slug_base)}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Orders"
        db_table = "orders"


class PastOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=50, choices=[('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')],
        default='Delivered'
    )
    delivery_date = models.DateField()
    cancelled_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Past Order {self.order.id} - {self.status}"
    
    class Meta:
        verbose_name_plural = "Past Orders"
        db_table = "past_orders"
    

class Contact(TimeStampedSoftDeleteModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    message = models.TextField(null=False, blank=False)

    # # Soft delete fields
    # is_deleted = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Contacts"
        db_table = "contacts"

    def __str__(self):
        return self.name
