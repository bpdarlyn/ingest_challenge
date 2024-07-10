from django.contrib import admin
from backend.api.models import Country, Industry, Organization

# Register your models here.
admin.site.register(Country)
admin.site.register(Industry)
admin.site.register(Organization)
