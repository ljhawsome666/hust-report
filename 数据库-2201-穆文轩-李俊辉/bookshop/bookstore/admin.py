from django.contrib import admin
from .models import Publisher, Book, Inventory, Customer, Shipment,OutOfStockBook
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Order, OrderBook

# 自定义 UserAdmin，定制显示字段
class CustomUserAdmin(UserAdmin):
    model = User
    # 显示的字段
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # 用户详情页面字段
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
    )


# 重新注册 auth.User 模型到 admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'price', 'stock_quantity')
    search_fields = ('title', 'authors')


# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'customer', 'order_date', 'total_amount', 'status')
#     list_filter = ('status',)
#     search_fields = ('customer__full_name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'created_at', 'total_amount', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__full_name', 'id')


@admin.register(OrderBook)
class OrderBookAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'total_price')
    search_fields = ('book__title',)


admin.site.register(Publisher)
admin.site.register(Book, BookAdmin)
admin.site.register(Inventory)
admin.site.register(Customer)
# admin.site.register(OrderItem)
admin.site.register(Shipment)
admin.site.register(OutOfStockBook)
# Register your models here.
