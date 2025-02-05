from django.urls import path
from .views import *


urlpatterns = [
    path('', Home.as_view(),name='home'),
    path('product-category/', ProductCategoryView.as_view(), name='product-category'),
    path('Product_categoryUpdate/<int:id>/', Product_categoryUpdate.as_view(), name='Product_categoryUpdate'),
    path('ProductListPost/', ProductListPost.as_view(), name='ProductListPost'),
    path('ProduclistView/', ProduclistView.as_view(), name='ProduclistView'),
    path('Register/', Register_custumer.as_view(), name='Register'),
    path('Login/', Login_view.as_view(), name='Login'),
    path('Logout/', Logout_view.as_view(), name='Logout'),
    path('Search_history/', Search_history.as_view(), name='Search_history'),
    # path('Add_cart/', Add_cart.as_view(), name='Add_cart'),
    path('Newly_arrived/', Newly_arrived.as_view(), name='Newly_arrived'),
    path('Profile_update/<int:id>/', Profile_update.as_view(), name='Profile_update'),
    path('Category_filter/', Category_filter.as_view(), name='Category_filter'),
    path('Product_updateanddelete/<int:id>/', Product_updateanddelete.as_view(), name='Product_updateanddelete'),

    path('Adding_cart/', Adding_cart.as_view(), name='Adding_cart'),








]