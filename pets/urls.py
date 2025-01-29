from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Login and Logout views
    path('login/', auth_views.LoginView.as_view(template_name='pets/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #path('login/', DebugLoginView.as_view(), name='login'),

    # Signup view
    path('register/', views.register, name='register'),

    # Other paths
    path("", views.pet_list, name="pet_list"),
    path("add_pet", views.add_pet, name="add_pet"),
    path("buy_items", views.buy_items, name="buy_items"),
    path("inventory", views.view_inventory, name="user_inventory"),
    path('use_item/<int:inventory_id>/<int:pet_id>/', views.use_item, name='use_item'),
    path('pet_details/<int:pet_id>/', views.pet_list, name='pet_details')

]