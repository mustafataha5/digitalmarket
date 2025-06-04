
from django.urls import path
from . import views 


app_name = 'main'

urlpatterns = [
    path('',views.index,name='index'),
    path('view/<int:id>',views.detail,name='detail'),
    path('add_to_cart',views.add_to_cart,name='add_to_cart'),
    path('delete_from_cart',views.delete_from_cart,name='delete_from_cart'),
    path('add_to_wishlist',views.add_to_wishlist,name='add_to_wishlist'),
    path('delete_from_wishlist',views.delete_from_wishlist,name='delete_from_wishlist'),
    path('show_list/',views.show_list,name='show_list'),
    
    path('pay/', views.fake_payment_page, name='fake-payment'),
    path('payment/success/', views.payment_success, name='payment-success'),
    
    path('orders',views.show_order,name="show_order"),
    path('orders/<int:id>',views.show_order_detail,name="show_order_detail"),
    
    path('create_product/',views.product_create,name='product_create'),
    path('edit_product/<int:id>',views.product_edit,name='product_edit'),
    path('delete_product/<int:id>',views.product_delete,name='product_delete'),
     
    path('dashbord',views.dashbord,name='dashboard'), 
    
    path('signup',views.register,name='register'),
    path('signin',views.custom_login_view,name='login'),
    path('logout',views.custom_logout_view,name='logout'),
    
    path('403',views.invalid,name="403"),
    
    path('sales',views.sales,name="sales"),
]
