from django.contrib import admin
from .models import ShippingAddress,Order,Orderitem
from django.contrib.auth.models import User


admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(Orderitem)


class OrderItemInline(admin.StackedInline):
    model=Orderitem
    extra=0


#Extend order Model

class OrderAdmin(admin.ModelAdmin):
    model=Order
    readonly_fields=["date_ordered"]
    fields=[
            "user",
            "full_name",
            "email",
            "shipping_address",
            "ammount_paid",
            "date_ordered",
            "shipped",
            "date_shipped"
        ]
    inlines=[OrderItemInline]

admin.site.unregister(Order)
admin.site.register(Order,OrderAdmin)
