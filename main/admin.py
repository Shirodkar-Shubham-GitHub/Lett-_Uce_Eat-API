from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Badge)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(PastOrder)
admin.site.register(Contact)
