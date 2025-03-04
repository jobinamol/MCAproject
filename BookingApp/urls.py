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
    path('dashboard/packages/add/', views.add_package, name='add_package'),
    path('dashboard/packages/<int:pk>/edit/', views.edit_package, name='edit_package'),
    path('dashboard/packages/<int:pk>/delete/', views.delete_package, name='delete_package'),
    path('dashboard/bookings/', views.manage_bookings, name='manage_bookings'),
    path('dashboard/rooms/', views.manage_rooms, name='manage_rooms'),
    path('dashboard/analytics/', views.analytics, name='analytics'),
    path('dashboard/reviews/', views.reviews, name='reviews'),
    path('dashboard/resort/', views.resort_home, name='resort_home'),
    
    # API endpoints
    path('api/update-pricing/', views.update_pricing, name='update_pricing'),
    path('api/analytics-data/', views.get_analytics_data, name='analytics_data'),
    
    # Room Management URLs
    path('dashboard/rooms/', views.manage_rooms, name='manage_rooms'),
    path('dashboard/rooms/add/', views.add_room, name='add_room'),
    path('dashboard/rooms/<int:pk>/edit/', views.edit_room, name='edit_room'),
    path('dashboard/rooms/<int:room_id>/bookings/', views.room_bookings, name='room_bookings'),
    path('dashboard/rooms/<int:room_id>/bookings/add/', views.add_booking, name='add_booking'),
    
    # Venue Management URLs
    path('dashboard/venues/', views.manage_venues, name='manage_venues'),
    path('dashboard/venues/add/', views.add_venue, name='add_venue'),
    path('dashboard/venues/<int:pk>/edit/', views.edit_venue, name='edit_venue'),
    path('dashboard/venues/<int:venue_id>/bookings/', views.venue_bookings, name='venue_bookings'),
    path('dashboard/venues/<int:venue_id>/bookings/add/', views.add_booking, name='add_booking'),
    
    # Food & Beverage Management URLs
    path('dashboard/menu/', views.manage_menu, name='manage_menu'),
    path('dashboard/menu/add/', views.add_menu_item, name='add_menu_item'),
    path('dashboard/menu/<int:pk>/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('dashboard/orders/', views.manage_orders, name='manage_orders'),
    path('dashboard/orders/add/', views.add_order, name='add_order'),
    path('dashboard/orders/<int:pk>/edit/', views.edit_order, name='edit_order'),
    
    # Settings and Authentication URLs
    path('dashboard/settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    
    # Demand Prediction URL
    path('dashboard/demand-prediction/', views.demand_prediction, name='demand_prediction'),
]
