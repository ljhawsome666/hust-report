from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User
from django.utils import timezone


# 出版社模型
class Publisher(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name


# 书籍模型
class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)  # 以逗号分隔的作者列表
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    keywords = models.CharField(max_length=255)  # 以逗号分隔的关键字
    stock_quantity = models.IntegerField(default=0)
    isbn = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.title


# 库存模型
class Inventory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField(default=0)
    shelf_location = models.CharField(max_length=255)

    def __str__(self):
        return f"Inventory for {self.book.title} at {self.shelf_location}"


# 客户模型
class Customer(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit_rating = models.CharField(
        max_length=1,
        choices=[('1', 'Level 1'), ('2', 'Level 2'), ('3', 'Level 3'), ('4', 'Level 4'), ('5', 'Level 5')],
    )

    def __str__(self):
        return self.full_name


# 订单状态常量
ORDER_STATUS_CHOICES = [
    ('pending', '待发货'),
    ('shipped', '已发货'),
    ('cancelled', '取消'),
]


# 订单模型
class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)  # 关联客户
    created_at = models.DateTimeField(auto_now_add=True)  # 订单创建时间
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 总钱数
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')  # 订单状态

    def __str__(self):
        return f"订单 #{self.id} - {self.customer.full_name} - {self.status}"

    # 计算总钱数
    def calculate_total_amount(self):
        self.total_amount = sum(item.total_price for item in self.orderbook_set.all())
        self.save()


# 订单书籍模型（多对多关系）
class OrderBook(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderbook_set')  # 关联订单
    book = models.ForeignKey('Book', on_delete=models.CASCADE)  # 关联书籍
    quantity = models.IntegerField(default=1)  # 订购数量
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # 单本书的总价（价格 * 数量）

    def save(self, *args, **kwargs):
        # 在保存时计算单本书的总价
        self.total_price = self.book.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - 数量: {self.quantity} - 总价: {self.total_price}"



# 发货模型
class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipment_date = models.DateField()
    tracking_number = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')])

    def __str__(self):
        return f"Shipment for Order {self.order.id}"


# 缺书模型
class OutOfStockBook(models.Model):
    book_title = models.CharField(max_length=255)  # 书名
    quantity = models.IntegerField(default=0)  # 缺书数量
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)  # 关联出版社
    registration_date = models.DateField(auto_now_add=True)  # 登记日期，自动获取当前日期

    def __str__(self):
        return f"{self.book_title} - {self.publisher.name} - {self.quantity} missing"
# Create your models here.
