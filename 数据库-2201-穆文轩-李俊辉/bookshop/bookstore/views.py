# bookstore/views.py
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from .models import Order, OrderBook, Book
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import Customer

@csrf_exempt
@login_required
def update_profile(request):
    if request.method == 'POST':
        print(11111)
        try:
            # 获取前端传递的数据
            data = json.loads(request.body)
            full_name = data.get('full_name')
            address = data.get('address')
            account_balance = float(data.get('account_balance'))

            # 获取当前登录的用户
            user = request.user

            # 获取当前用户的 Customer 对象
            customer = Customer.objects.get(username=user.username)
            print(222)
            # 更新用户信息
            customer.full_name = full_name
            customer.address = address
            customer.account_balance = account_balance

            # 根据账户余额更新信用评级
            if account_balance < 100:
                customer.credit_rating = '1'
            elif 100 <= account_balance < 500:
                customer.credit_rating = '2'
            elif 500 <= account_balance < 1000:
                customer.credit_rating = '3'
            elif 1000 <= account_balance < 5000:
                customer.credit_rating = '4'
            else:
                customer.credit_rating = '5'

            # 保存用户信息
            customer.save()

            return JsonResponse({'success': True})

        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Customer not found'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)




# # 生成订单视图
# @login_required
# def create_order(request, book_id):
#     # 获取当前用户
#     user = request.user
#
#     # 获取所选的书籍
#     book = Book.objects.get(id=book_id)
#
#     # 创建订单
#     order = Order.objects.create(
#         customer=user.customer,  # 通过用户获取客户实例
#         order_date=timezone.now(),
#         total_amount=book.price,  # 订单总金额（此处简单计算，实际可以根据购买数量计算）
#         status='pending',  # 订单状态：待处理
#         shipping_address=user.customer.address  # 订单收货地址
#     )
#
#     # 创建订单项
#     OrderItem.objects.create(
#         order=order,
#         book=book,
#         quantity=1,  # 假设每次购买 1 本书
#         price=book.price
#     )
#
#     # 返回订单成功页面或重定向到订单信息页
#     return redirect('order_details', order_id=order.id)
#
#
# @login_required
# def order_details(request, order_id):
#     user = request.user
#     # 获取指定订单
#     order = get_object_or_404(Order, id=order_id, customer=user.customer)
#
#     # 获取订单中的所有项（即该订单包含的书籍）
#     order_items = OrderItem.objects.filter(order=order)
#
#     # 渲染模板并传递订单和订单项的数据
#     return render(request, 'bookstore/order_detail.html', {
#         'order': order,
#         'order_items': order_items
#     })


@login_required
def search_books(request):
    print(1)
    query = request.GET.get('q', '')  # 获取查询参数 q
    print(query)
    if query:
        # 使用模糊查询来查找书籍
        books = Book.objects.filter(title__icontains=query)  # 或者你可以按需要做其他查询
        book_list = [{"id": book.id, "title": book.title} for book in books]
        return JsonResponse({"books": book_list})  # 返回找到的书籍列表
    else:
        return JsonResponse({"error": "No query parameter provided."}, status=400)


def book_details(request, book_id):
    try:
        # book = Book.objects.get(id=book_id)
        book = Book.objects.select_related('publisher').get(id=book_id)
        # 序列化书籍信息
        # 获取与该书籍相关联的出版社数据
        publisher = book.publisher
        book_data = {
            'id': book.id,
            'title': book.title,
            'authors': book.authors,
            # 'publisher': {
            #     'id': book.publisher.id,
            #     'name': book.publisher.name,  # 假设 Publisher 有 name 字段
            # },
            'publisher': {
                'name': book.publisher.name,
                'address': book.publisher.address,
                'contact_number': book.publisher.contact_number
            },
            'price': book.price,
            'stock': book.stock_quantity,
        }
        return JsonResponse(book_data)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)


def home(request):
    return render(request, 'bookstore/home.html')


def library_home(request):
    return render(request, 'bookstore/library_home.html')
# 登录视图

class CustomLoginView(LoginView):
    template_name = 'bookstore/login.html'


# 注册视图
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # 保存新用户信息
            form.save()
            # 自动登录用户
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('login')  # 重定向到首页或其他页面
    else:
        form = CustomUserCreationForm()
    return render(request, 'bookstore/register.html', {'form': form})
# home 视图会渲染一个名为 home.html 的模板。
# Create your views here.


@csrf_exempt  # 如果你是从前端使用 POST 请求，添加这个装饰器
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            # customer = request.user.customer  # 假设用户已登录
            user = request.user

            # 获取当前用户的 Customer 对象
            customer = Customer.objects.get(username=user.username)
            # 创建订单
            order = Order.objects.create(customer=customer, total_amount=0)
            total_amount = 0

            # 遍历购物车中的商品，创建订单项
            for item in cart:
                book = Book.objects.get(id=item['bookId'])
                quantity = int(item['quantity'])
                total_price = book.price * quantity
                total_amount += total_price

                # 创建订单书籍项
                OrderBook.objects.create(order=order, book=book, quantity=quantity, total_price=total_price)

            # 更新订单总金额
            order.total_amount = total_amount
            order.save()

            # 返回成功信息和订单ID
            return JsonResponse({
                "success": True,
                "order_id": order.id,
                "message": "订单创建成功"
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": str(e)
            })
    return JsonResponse({
        "success": False,
        "message": "请求方法不正确"
    })


@login_required
def checkout(request):
    # 获取当前登录用户
    # customer = request.user.customer
    user = request.user

    # 获取当前用户的 Customer 对象
    customer = Customer.objects.get(username=user.username)
    # 获取购物车中的书籍和数量
    cart = request.session.get('cart', [])

    if not cart:
        return JsonResponse({'error': '购物车为空，无法结账'}, status=400)

    # 创建订单
    order = Order.objects.create(
        customer=customer,
        total_amount=0,  # 初始时总金额为0
        status='pending',  # 初始状态为待支付
    )

    total_amount = 0

    # 创建订单中的书籍
    for item in cart:
        book = item['book']
        quantity = item['quantity']
        total_price = book.price * quantity

        # 创建 OrderBook 关联订单和书籍
        order_book = OrderBook.objects.create(
            order=order,
            book=book,
            quantity=quantity,
            total_price=total_price,
        )

        # 累加总金额
        total_amount += total_price

    # 更新订单的总金额
    order.total_amount = total_amount
    order.save()

    # 清空购物车
    request.session['cart'] = []

    return JsonResponse({'success': '订单生成成功', 'order_id': order.id})


@login_required
def order_list(request):
    # customer = request.user.customer
    # 获取当前登录的用户
    user = request.user

    # 获取当前用户的 Customer 对象
    customer = Customer.objects.get(username=user.username)
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'bookstore/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    user = request.user
    order = Order.objects.get(id=order_id, customer = Customer.objects.get(username=user.username))
    order_books = OrderBook.objects.filter(order=order)
    return render(request, 'bookstore/order_detail.html', {'order': order, 'order_books': order_books})