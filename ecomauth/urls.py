from django.urls import path    
from ecomauth import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.handlelogin, name='handlelogin'),
    path('logout/', views.handlelogout, name='handlelogout'),
    path('activate/<str:uidb64>/<str:token>/', views.ActivateAccountView.as_view(), name='activate'),
    path('request-reset-email/', views.RequestResetEmailView.as_view(), name = 'request-reset-email'),
    path('set-new-password/<str:uidb64>/<str:token>/', views.SetNewPasswordView.as_view(), name = 'set-new-password'),
]