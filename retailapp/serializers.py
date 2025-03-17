from rest_framework import serializers
from .models import *
from django.conf import settings


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Category
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_list
        fields = '__all__'


class Register_custumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_items
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order_products
        fields = '__all__'


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'

class Slider_Add_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Slider_Add
        fields = ['slider_image']