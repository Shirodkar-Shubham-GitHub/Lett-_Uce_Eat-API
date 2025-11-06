from .models import *
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])


    class Meta:

        model = CustomUser
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):

        user = CustomUser.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )

        return user

class HeroPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MenuItem
        fields = ['id', 'image', 'name', 'price', 'slug']    #    , 'cuisine'

class DishDetailsPageSerializer(serializers.ModelSerializer):

    menu_item = HeroPageSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menu_item', 'total_price', 'quantity']    #    , 'cuisine'


class CartSerializer(serializers.ModelSerializer):
    menu_item = HeroPageSerializer(read_only=True)
    # total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'menu_item', 'quantity']


class OrderSerializer(serializers.ModelSerializer):

    # customer = serializers.PrimaryKeyRelatedField(read_only=True)
    # total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'dish', 'quantity', 'total_price', 'calculate_total_price', 'status', 'created_at', 'razorpay_order_id']

    def create(self, validated_data):
        cart_items = validated_data.get('cart_items')
        # Create an order from cart items (create multiple orders if needed)
        orders = []
        for cart_item in cart_items:
            order = Order.objects.create(
                user=validated_data['user'],
                dish=cart_item.menu_item,
                quantity=cart_item.quantity,
                total_price=cart_item.total_price(),
            )
            orders.append(order)
        return orders     

    # def get_total_amount(self, obj):
    #     return sum(item.get_total_price() for item in obj.items.all())

    def validate(self, validated_data):

        if not validated_data['status']:
            raise serializers.ValidationError('Status field is required')

        return validated_data   

    def get_total_cart_price(self, obj):
        user = obj.user
        cart_items = Cart.objects.filter(user=user, is_deleted=False)
        total_price = sum(item.quantity * item.menu_item.price for item in cart_items if item.menu_item)
        return total_price


class PastOrderSerializer(serializers.ModelSerializer):

    # customer = serializers.PrimaryKeyRelatedField(read_only=True)
    # total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'dish', 'quantity', 'total_price', 'calculate_total_price', 'status', 'updated_at']

    # def create(self, validated_data):
    #     cart_items = validated_data.get('cart_items')
    #     # Create an order from cart items (create multiple orders if needed)
    #     orders = []
    #     for cart_item in cart_items:
    #         order = Order.objects.create(
    #             user=validated_data['user'],
    #             dish=cart_item.menu_item,
    #             quantity=cart_item.quantity,
    #             total_price=cart_item.total_price(),
    #         )
    #         orders.append(order)
    #     return orders     

    # def get_total_amount(self, obj):
    #     return sum(item.get_total_price() for item in obj.items.all())

    def validate(self, validated_data):

        if not validated_data['status']:
            raise serializers.ValidationError('Status field is required')

        return validated_data   

    def get_total_cart_price(self, obj):
        user = obj.user
        cart_items = Cart.objects.filter(user=user, is_deleted=False)
        total_price = sum(item.quantity * item.menu_item.price for item in cart_items if item.menu_item)
        return total_price

# class CartItemSerializer(serializers.ModelSerializer):
#     menu_item = DishDetailsPageSerializer(read_only=True)  # Serialize dish details
#     total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

#     class Meta:
#         model = CartItem
#         fields = ['id', 'menu_item', 'quantity', 'total_amount']


# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True)
#     total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

#     class Meta:
#         model = Cart
#         fields = ['id', 'user', 'items', 'total_amount']

# class ActiveOrdersSerializer(serializers.ModelSerializer):

#     menu_item = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = OrderItem
#         fields = ['id', 'menu_item', 'quantity']


class MenuItemSerializer(serializers.ModelSerializer):

    badges = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Badge.objects.all()
    )

    class Meta:
        model = MenuItem
        fields = ['id', 'image', 'name', 'price', 'is_available', 'cuisine', 'diet_type', 'badges', 'slug']

    # def validate(self, validated_data):
    #     if not validated_data['image']:
    #         raise serializers.ValidationError('Image field is required')
    #     if not validated_data['name']:
    #         raise serializers.ValidationError('Name field is required')
    #     if not validated_data['price']:
    #         raise serializers.ValidationError('Price field is required')
    #     if 'is_available' not in validated_data:
    #         raise serializers.ValidationError('Availability field is required')
        
        # return validated_data

# class OrderSerializer(serializers.ModelSerializer):

#     customer = serializers.PrimaryKeyRelatedField(read_only=True)
#     total_amount = serializers.SerializerMethodField()

#     class Meta:
#         model = Order
#         fields = ['id', 'customer', 'menu_item', 'status', 'total_amount']

#     def get_total_amount(self, obj):
#         return sum(item.get_total_price() for item in obj.items.all())

#     def validate(self, validated_data):

#         if not validated_data['status']:
#             raise serializers.ValidationError('Status field is required')

#         return validated_data


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'message']

    def validate(self, validated_data):

        if not validated_data['name']:
            raise serializers.ValidationError('Name field is required')
        if not validated_data['email']:
            raise serializers.ValidationError('Email field is required')
        if not validated_data['message']:
            raise serializers.ValidationError('Message field is required')
        
        return validated_data
