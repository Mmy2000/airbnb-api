from django.contrib import admin
from .models import Property , Reservation , PropertyImages


admin.site.register(Property)
admin.site.register(Reservation)
admin.site.register(PropertyImages)