# bookstore/urls.py
from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # 设置初始页面路由
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('search_books/', views.search_books, name='search_books'),
    path('', views.library_home, name='library_home'),  # 登录后进入 library_home
    path('book/<int:book_id>/', views.book_details, name='book_details'),
    # path('order/<int:order_id>/', views.order_details, name='order_details'),  # 查看订单详情
    path('update_profile/', views.update_profile, name='update_profile'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_list/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('create_order/', views.create_order, name='create_order'),
]


