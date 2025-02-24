from django.urls import path
from .views import (
    home, 
    recommend_view, 
    recommend_page,
    dashboard,
    manage_packages,
    manage_bookings,
    analytics,
    reviews
)

urlpatterns = [
    # Public routes
    path('', home, name='home'),
    path('recommend/', recommend_view, name='recommend_api'),
    path('recommend/results/', recommend_page, name='recommend_page'),
    
    # Dashboard routes
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/packages/', manage_packages, name='manage_packages'),
    path('dashboard/bookings/', manage_bookings, name='manage_bookings'),
    path('dashboard/analytics/', analytics, name='analytics'),
    path('dashboard/reviews/', reviews, name='reviews'),
]
