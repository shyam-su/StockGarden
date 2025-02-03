from django.urls import path
from .views import *


urlpatterns = [
    path('login/', LoginView, name='login'),
    path('logout/', LogoutView, name='logout'),
    
          # Customer URLs
    path('user/', UserListView, name='user'),
    path('user/create/', UserCreateView,name='user_create'),
    path('user/<int:pk>/update/', UserUpdateView,name='user_update'),
    path('user/<int:pk>/delete/', UserDeleteView,name='user_delete'),

]

