from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register-user'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('update_profile/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('top_users/', views.TopUsersView.as_view(), name='top-users'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
