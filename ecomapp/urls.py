from django.urls import path
from ecomapp import views

urlpatterns = [
    path('',views.home, name='home'),
    path('purchase', views.purchase, name='purchase'),
    path('tracker/', views.tracker, name="Trackinstatus"),
    path('checkout/', views.checkout, name='Checkout'),
    path('handlerequest/', views.handlerequest, name='HandleRequest'),
    
]