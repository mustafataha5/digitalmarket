from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout # Import the login function
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum ,Count,F,Q
import datetime
from .models import Product ,Cart ,Wishlist,OrderItem,Order
from django.db import transaction
from django.contrib import messages

from .forms import ProductForm,RegistrationForm,LoginForm
# Create your views here.



def index(request): 
    
    products = Product.objects.all() ; 
    
    
    data = {
        'products':products , 
    }
    
    return render(request,'index.html',data)


def detail(request,id): 
    product = get_object_or_404(Product,id=id)
    
    wishlist_product_ids = []

    if request.user.is_authenticated:
        wishlist_product_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        cart_product_ids = Cart.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    data = {
        'product':product ,
        'in_cart': product.id in cart_product_ids ,
        'in_wishlist': product.id in wishlist_product_ids , 
    }
    
    return render(request,'details.html',data)

@login_required
def add_to_cart(request):
    if request.method == 'POST': 
        user = request.user 
        product_id = request.POST['product_id']
        product = get_object_or_404(Product,id=product_id)
        from_url = int(request.POST['from_url'])
        product_quantity = int(request.POST['product_quantity'])
        if product_quantity >= 1 and product_quantity <= 10 : 
            Cart.objects.create(user=user, product=product,quantity=product_quantity)
            Wishlist.objects.filter(user=user, product=product).delete()
            messages.success(request,f'Successfull Add {product.name} X f{product_quantity}') 
        else: 
            messages.error(request,'product quantity must be  >= 1 and  <= 10 ') 
            data = {
                'product':product , 
            }
            return render(request,'details.html',data)
    if( from_url == 1):
        return redirect('main:detail', id=product.id) 
    else:
        return redirect('main:show_list')
    
@login_required
def delete_from_cart(request):
    if request.method == 'POST': 
        user = request.user 
        product_id = request.POST['product_id']
        product = get_object_or_404(Product,id=product_id)
        from_url = int(request.POST['from_url'])
        Cart.objects.filter(user=user,product=product).delete()
        
    if( from_url == 1):
        return redirect('main:detail', id=product.id) 
    else:
        return redirect('main:show_list')    

@login_required
def add_to_wishlist(request):
    if request.method == 'POST': 
        user = request.user 
        product_id = request.POST['product_id']
        product = get_object_or_404(Product,id=product_id)
        Wishlist.objects.create(user=user, product=product)
    
    return redirect('main:detail', id=product.id) 




@login_required
def delete_from_wishlist(request):
    if request.method == 'POST': 
        user = request.user 
        # Wishlist.objects.get(id,request.POST['wishlist_item_id']).delete()
        product_id = request.POST['product_id']
        product = get_object_or_404(Product,id=product_id)
        Wishlist.objects.filter(user=user, product=product).delete()
        from_url = int(request.POST['from_url'])
    if (from_url == 1):    
        return redirect('main:detail', id=product.id) 
    else: 
        return redirect('main:show_list')


@login_required
def show_list(request): 
    user = request.user
    wishlist_products= Wishlist.objects.filter(user=user)
    cart_products = Cart.objects.filter(user=user)
    total_cart_price = sum(item.total_price() for item in cart_products)
    print(total_cart_price)
    data = {
        'wishlist_products':wishlist_products,
        'cart_products':cart_products,
        'total_cart_price':total_cart_price,
    }
    
    return render(request,'cart_and_list.html',data)



@login_required
def fake_payment_page(request):
    if request.method == 'POST':
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            return redirect('main:show_list')  # or show a "Cart is empty" message

        total_cart_price = sum(item.total_price() for item in cart_items)

        try:
            with transaction.atomic():  # ensures atomic operation
                # Create the order
                order = Order.objects.create(
                    user=user,
                    total_amount=total_cart_price,
                    status='processing' #'pending'  # or 'processing' if you prefer
                )

                # Create OrderItems
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price  # store current price
                    )

                # Clear the cart
                cart_items.delete()

        except Exception as e:
            print("Order creation failed:", e)
            return redirect('main:show_list')  # optionally pass error message

        return redirect('main:payment-success')  # or show order summary

    return render(request, 'fake_payment.html')

@login_required
def payment_success(request):
    return render(request, 'payment_success.html')

@login_required
def show_order(request):
    user = request.user 
    orders = Order.objects.filter(user=user)
    data={
        'orders':orders , 
    }
    return render(request,'order.html',data)

@login_required
def show_order_detail(request,id):
    user = request.user 
    orders = Order.objects.get(id=id,user=user)
    data={
        'order':orders , 
    }
    return render(request,'order_detail.html',data)

@login_required
def product_create(request):
    if request.method == "POST": 
        form = ProductForm(request.POST,request.FILES) 
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('main:index') 
    else:     
        form = ProductForm()
    data = {
        'form':form,
        'title':"Create",
    }
    return render(request,'product_form.html',data)


@login_required
def product_edit(request, id):
    user = request.user
    try:
        product = Product.objects.get(id=id, seller=user)
    except Product.DoesNotExist:
        return redirect('main:403')

    if request.method == "POST": 
        form = ProductForm(request.POST, request.FILES, instance=product) 
        if form.is_valid():
            form.save()
            return redirect('main:index') 
    else:     
        form = ProductForm(instance=product)
    data = {
        'form': form,
        'title': "Edit",
        'product': product,
    }
    return render(request, 'product_form.html', data)


@login_required
def product_delete(request, id):
    user = request.user
    try:
        product = Product.objects.get(id=id, seller=user)
    except Product.DoesNotExist:
        return redirect('main:403')

    if request.method == "POST": 
        product.delete()
        return redirect('main:index')
    return redirect('main:product_edit', id=id)

@login_required
def dashbord(request): 
    user = request.user
    products = Product.objects.filter(seller=user) ; 
    data = {
        'products':products , 
    }
    return render(request,'dashboard.html',data)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save() # This creates the user
            login(request, user) # Automatically log in the user after registration
            # Redirect to a success page, e.g., a profile page or the homepage
            return redirect('main:index') # Adjust 'main:index' to your actual home URL name
    else:
        form = RegistrationForm()

    context = {
        'form': form,
        'title': 'Register',
        'btn_text': 'Sign Up', # Renamed 'btn_' to 'btn_text' for clarity
    }
    return render(request, 'user_form.html', context)


def custom_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:index')  # Change 'home' to your actual homepage URL name
    else:
        form = LoginForm()

    return render(request, 'user_form.html', {'form': form, 'title': 'Login', 'btn_text': 'Sign In'})




@login_required
@csrf_protect
def custom_logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('main:index')
    return redirect('main:index') 


def invalid(request):
    return render(request,'403.html')


@login_required

def sales(request):
    today = datetime.date.today()
    annual_start = today - datetime.timedelta(days=365)
    monthly_start = today - datetime.timedelta(days=30)
    weekly_start = today - datetime.timedelta(days=7)
    daily_start = today - datetime.timedelta(days=1)

    products_queryset = Product.objects.filter(seller=request.user).annotate(
        number_of_sales=Sum('orderitem__quantity'),
        number_of_orders=Count('orderitem__order', distinct=True),
        total_sales_price=Sum(F('orderitem__quantity') * F('orderitem__price')),

        annual_sales=Sum(
            'orderitem__quantity',
            filter=Q(orderitem__order__created_at__gte=annual_start)
        ),
        monthly_sales=Sum(
            'orderitem__quantity',
            filter=Q(orderitem__order__created_at__gte=monthly_start)
        ),
        weekly_sales=Sum(
            'orderitem__quantity',
            filter=Q(orderitem__order__created_at__gte=weekly_start)
        ),
        daily_sales=Sum(
            'orderitem__quantity',
            filter=Q(orderitem__order__created_at__gte=daily_start)
        ),

        annual_revenue=Sum(
            F('orderitem__quantity') * F('orderitem__price'),
            filter=Q(orderitem__order__created_at__gte=annual_start)
        ),
        monthly_revenue=Sum(
            F('orderitem__quantity') * F('orderitem__price'),
            filter=Q(orderitem__order__created_at__gte=monthly_start)
        ),
        weekly_revenue=Sum(
            F('orderitem__quantity') * F('orderitem__price'),
            filter=Q(orderitem__order__created_at__gte=weekly_start)
        ),
        daily_revenue=Sum(
            F('orderitem__quantity') * F('orderitem__price'),
            filter=Q(orderitem__order__created_at__gte=daily_start)
        ),
    )

    # --- Convert QuerySet to a serializable list of dictionaries ---
    products_list = []
    for product in products_queryset:
        product_dict = {
            'id': product.id,
            'name': product.name,
            'desc': product.desc,
            'number_of_sales': product.number_of_sales,
            'number_of_orders': product.number_of_orders,
            'total_sales_price': float(product.total_sales_price) if product.total_sales_price is not None else 0.0, # Convert Decimal to float
            'annual_sales': product.annual_sales,
            'monthly_sales': product.monthly_sales,
            'weekly_sales': product.weekly_sales,
            'daily_sales': product.daily_sales,
            'annual_revenue': float(product.annual_revenue) if product.annual_revenue is not None else 0.0,
            'monthly_revenue': float(product.monthly_revenue) if product.monthly_revenue is not None else 0.0,
            'weekly_revenue': float(product.weekly_revenue) if product.weekly_revenue is not None else 0.0,
            'daily_revenue': float(product.daily_revenue) if product.daily_revenue is not None else 0.0,
        }
        products_list.append(product_dict)

    context = {
        'products': products_queryset, # Keep original QuerySet for table rendering
        'products_data_for_chart': products_list, # New context variable for chart data
    }
    return render(request, 'sales.html', context)




