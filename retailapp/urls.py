from django.urls import path
from .views import *


urlpatterns = [
    path('', Home.as_view(),name='home'),
    path('api/product-category/', ProductCategoryView.as_view(), name='product-category'),
    path('api/Product_categoryUpdate/<int:id>/', Product_categoryUpdate.as_view(), name='Product_categoryUpdate'),
    path('api/ProductListPost/', ProductListPost.as_view(), name='ProductListPost'),
    # path('api/ProduclistView/', ProduclistView.as_view(), name='ProduclistView'),
    path('api/Register/', Register_custumer.as_view(), name='Register'),
    path('api/Login/', Login_view.as_view(), name='Login'),
    path('api/Logout/', Logout_view.as_view(), name='Logout'),
    path('api/Search_history/', Search_history.as_view(), name='Search_history'),
    # path('Add_cart/', Add_cart.as_view(), name='Add_cart'),
    path('api/Newly_arrived/', Newly_arrived.as_view(), name='Newly_arrived'),
    path('api/Profile_update_custumer/<int:id>/', Profile_update_custumer.as_view(), name='Profile_update_custumer'),
    path('api/Category_filter/', Category_filter.as_view(), name='Category_filter'),
    path('api/Product_updateanddelete/<int:id>/', Product_updateanddelete.as_view(), name='Product_updateanddelete'),
    path('api/Adding_cart/', Adding_cart.as_view(), name='Adding_cart'),
    path('api/Delete_all_cart/', Delete_all_cart.as_view(), name='Delete_all_cart'),
    path('api/order_products/', order_products.as_view(), name='order_products'),
    path('api/Update_order_status/', UpdateOrderStatus.as_view(), name='Update_order_status'),
    path('api/Total_counts_dashboard/', Total_counts_dashboard.as_view(), name='Total_counts_dashboard'),
    path('api/Update_customer_status/<int:id>/', Update_customer_status.as_view(), name='Update_customer_status'),
    path('api/Total_orders_list/', Total_orders_list.as_view(), name='Total_orders_list'),
    path('api/Search_all/', Search_all.as_view(), name='Search_all'),
    path('api/SearchAllCustomer/', SearchAllCustomer.as_view(), name='SearchAllCustomer'),
    path('api/CancelOrder/', CancelOrder.as_view(), name='CancelOrder'),
    path('api/Enquiry_send/', Enquiry_send.as_view(), name='Enquiry_send'),
    


]