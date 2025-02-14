from django.contrib import admin
from .models import Payment

# Register your models here.
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount", "status", "stripe_payment_intent")
    search_fields = ("order__id", "stripe_payment_intent", "status")
    list_filter = ("status",)
    ordering = ("-id",)
    readonly_fields = ()

admin.site.register(Payment, PaymentAdmin)