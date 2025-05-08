from django.contrib import admin
from .models import Product, Category, Order

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('category',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'get_products')
    
    def get_products(self, obj):
        return ", ".join([p.name for p in obj.products.all()])
    get_products.short_description = 'Products'

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
