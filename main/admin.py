from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DeliveryAddress)
admin.site.register(Contact)
