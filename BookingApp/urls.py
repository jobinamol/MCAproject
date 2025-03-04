from django.urls import path
from . import views

urlpatterns = [
    # Public routes
    path('', views.home, name='home'),
    path('recommend/', views.recommend_view, name='recommend_api'),
    path('recommend/results/', views.recommend_page, name='recommend_page'),
    
    # Dashboard routes
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/packages/', views.manage_packages, name='manage_packages'),
    path('dashboard/bookings/', views.manage_bookings, name='manage_bookings'),
    path('dashboard/rooms/', views.manage_rooms, name='manage_rooms'),
    path('dashboard/analytics/', views.analytics, name='analytics'),
    path('dashboard/reviews/', views.reviews, name='reviews'),
    path('dashboard/resort/', views.resort_home, name='resort_home'),
    
    # API endpoints
    path('api/update-pricing/', views.update_pricing, name='update_pricing'),
    path('api/analytics-data/', views.get_analytics_data, name='analytics_data'),
    
]
