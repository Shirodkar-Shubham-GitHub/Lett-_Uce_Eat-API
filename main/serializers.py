from .models import *
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])


    class Meta:

        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'phone']

    def create(self, validated_data):

        user = CustomUser.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password'],
            phone = validated_data['phone']
        )

        return user

    # def validate_phone(self, value):
    #     if CustomUser.objects.filter(phone=value).exists():
    #         raise serializers.ValidationError("Phone number already registered.")
    #     return value
    

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'auth_token', 'is_verified']

    def validate_auth_token(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("Auth token must be at least 20 characters long.")
        return value

    def validate(self, validated_data):
        if not validated_data['is_verified']:
            raise serializers.ValidationError('Verification is required')
        
        return validated_data


class HeroPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'image']

    def validate(self, validated_data):
        if not validated_data['name']:
            raise serializers.ValidationError('Name is required')
        
        if not validated_data['price']:
            raise serializers.ValidationError('Price is required')
        
        if not validated_data['image']:
            raise serializers.ValidationError('Image is required')
        
        return validated_data


class ActiveOrdersSerializer(serializers.ModelSerializer):

    menu_item = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity']


class MenuItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'is_available', 'image']

    def validate(self, validated_data):
        if not validated_data['name']:
            raise serializers.ValidationError('Name field is required')
        if not validated_data['description']:
            raise serializers.ValidationError('Description field is required')
        if not validated_data['price']:
            raise serializers.ValidationError('Price field is required')
        if not validated_data['is_available']:
            raise serializers.ValidationError('Availability field is required')
        if not validated_data['image']:
            raise serializers.ValidationError('Image field is required')
        
        return validated_data

class OrderSerializer(serializers.ModelSerializer):

    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'total_amount']

    def get_total_amount(self, obj):
        return sum(item.get_total_price() for item in obj.items.all())

    def validate(self, validated_data):

        if not validated_data['status']:
            raise serializers.ValidationError('Status field is required')

        # if not validated_data['total_amount']:
        #     raise serializers.ValidationError('Total amount field is required')

        return validated_data

class OrderItemSerializer(serializers.ModelSerializer):

    order = serializers.PrimaryKeyRelatedField(read_only=True)
    menu_item = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'price']

    def validate(self, validated_data):

        if not validated_data['quantity']:
            raise serializers.ValidationError('Quantity field is required')
        if not validated_data['price']:
            raise serializers.ValidationError('Price field is required')
        
        return validated_data
    

class DeliveryAddressSerializer(serializers.ModelSerializer):

    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DeliveryAddress
        fields = ['id', 'customer', 'order', 'address', 'city', 'postal_code', 'contact_phone']

    def validate(self, validated_data):

        if not validated_data['address']:
            raise serializers.ValidationError('Address field is required')
        if not validated_data['city']:
            raise serializers.ValidationError('City field is required')
        if not validated_data['postal_code']:
            raise serializers.ValidationError('Postal code field is required')
        if not validated_data['contact_phone']:
            raise serializers.ValidationError('Contact phone field is required')
        
        return validated_data


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'message']

    def validate(self, validated_data):

        if not validated_data['name']:
            raise serializers.ValidationError('Name field is required')
        if not validated_data['email']:
            raise serializers.ValidationError('Email field is required')
        if not validated_data['message']:
            raise serializers.ValidationError('Message field is required')
        
        return validated_data
    
    # def validate_phone(self, value):
    #     if CustomUser.objects.filter(phone=value).exists():
    #         raise serializers.ValidationError("Phone number already registered.")
    #     return value
