from django.contrib.auth.signals import user_logged_in  # 从正确的位置导入
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Customer


@receiver(user_logged_in)
def create_customer_on_login(sender, request, user, **kwargs):
    # 检查是否已经存在该用户的 Customer 对象，如果不存在，则创建
    if not Customer.objects.filter(username=user.username).exists():
        Customer.objects.create(
            username=user.username,
            password=user.password,  # 如果需要加密密码，可以用 make_password
            full_name=user.first_name,  # 假设 first_name 存储的是客户的姓名
            address=user.last_name,  # 假设 last_name 存储的是客户的地址
        )
