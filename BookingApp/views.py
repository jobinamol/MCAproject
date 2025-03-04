from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .utils import recommend_resorts
from datetime import datetime, timedelta
from django.utils import timezone
import json
import random  # For demo data, replace with actual data in production
from django.contrib import messages
from .models import Package, Activity, PackageActivity, PackageBooking, Room, RoomCategory, RoomBooking, Venue, VenueBooking
from .forms import PackageForm, ActivityForm, PackageActivityForm, ActivityFormSet, RoomForm, RoomCategoryForm, RoomBookingForm, VenueForm, VenueBookingForm

def home(request):
    """Render the home page."""
    return render(request, 'home.html')

def recommend_page(request):
    """Render the recommendations page."""
    return render(request, 'recommend.html')

def recommend_view(request):
    """API endpoint to provide resort recommendations."""
    hotel_name = request.GET.get('hotel', '').strip()
    # Add your recommendation logic here
    recommendations = recommend_resorts(hotel_name) if hotel_name else []
    return JsonResponse({'recommendations': recommendations})

def dashboard(request):
    """Render the main dashboard."""
    # Get package statistics
    active_packages = Package.objects.filter(status='active').count()
    inactive_packages = Package.objects.filter(status='inactive').count()
    seasonal_packages = Package.objects.filter(status='seasonal').count()
    total_packages = Package.objects.count()
    recent_packages = Package.objects.order_by('-created_at')[:5]

    # Get room statistics
    rooms = Room.objects.all()
    total_rooms = rooms.count()
    available_rooms = rooms.filter(status='available').count()
    occupied_rooms = rooms.filter(status='occupied').count()
    maintenance_rooms = rooms.filter(status='maintenance').count()
    
    # Get recent bookings
    recent_bookings = RoomBooking.objects.select_related('room').order_by('-created_at')[:5]

    context = {
        'active_packages_count': active_packages,
        'inactive_packages_count': inactive_packages,
        'seasonal_packages_count': seasonal_packages,
        'total_packages': total_packages,
        'recent_packages': recent_packages,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'dashboard/resort_index.html', context)

def manage_packages(request):
    packages = Package.objects.all().order_by('-created_at')
    today = timezone.now().date()
    
    # Add availability information
    for package in packages:
        package.is_available_today = package.is_available(today)
        package.available_slots = (
            package.daily_limit - PackageBooking.objects.filter(
                package=package,
                booking_date=today
            ).count()
        ) if package.daily_limit > 0 else None
    
    return render(request, 'dashboard/manage_packages.html', {'packages': packages})

def add_package(request):
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        activity_formset = ActivityFormSet(request.POST, prefix='activities')
        
        if form.is_valid() and activity_formset.is_valid():
            package = form.save()
            activity_formset.instance = package
            activity_formset.save()
            
            messages.success(request, 'Package added successfully!')
            return redirect('manage_packages')
    else:
        form = PackageForm()
        activity_formset = ActivityFormSet(prefix='activities')
    
    return render(request, 'dashboard/package_form.html', {
        'form': form,
        'activity_formset': activity_formset,
        'action': 'Add'
    })

def edit_package(request, pk):
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES, instance=package)
        activity_formset = ActivityFormSet(request.POST, instance=package, prefix='activities')
        
        if form.is_valid() and activity_formset.is_valid():
            form.save()
            activity_formset.save()
            messages.success(request, 'Package updated successfully!')
            return redirect('manage_packages')
    else:
        form = PackageForm(instance=package)
        activity_formset = ActivityFormSet(instance=package, prefix='activities')
    
    return render(request, 'dashboard/package_form.html', {
        'form': form,
        'activity_formset': activity_formset,
        'action': 'Edit'
    })

def delete_package(request, pk):
    package = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        package.delete()
        messages.success(request, 'Package deleted successfully!')
        return redirect('manage_packages')
    return render(request, 'dashboard/package_confirm_delete.html', {'package': package})

def manage_bookings(request):
    """Handle booking management."""
    bookings = [
        {
            'id': 'BK001',
            'guest_name': 'John Doe',
            'package': 'Luxury Villa',
            'check_in': datetime.now() + timedelta(days=2),
            'check_out': datetime.now() + timedelta(days=5),
            'status': 'Confirmed',
            'total_amount': 5999
        }
    ]
    return render(request, 'dashboard/bookings.html', {'bookings': bookings})

def analytics(request):
    """Show guest analytics and insights with date filtering."""
    # Get date range from request
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Default to last 30 days if no dates provided
    if not start_date or not end_date:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Get property filter
    property_id = request.GET.get('property', 'all')

    # Generate analytics data based on date range
    context = generate_analytics_data(start_date, end_date, property_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(context)
    
    return render(request, 'dashboard/analytics.html', context)

def generate_analytics_data(start_date, end_date, property_id='all'):
    """Generate analytics data for the given date range."""
    # Calculate date difference
    date_diff = (end_date - start_date).days
    
    # Generate daily data points
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'revenue': generate_revenue_data(current_date),
            'bookings': generate_booking_data(current_date),
            'occupancy': generate_occupancy_data(current_date)
        })
        current_date += timedelta(days=1)

    return {
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'days': date_diff
        },
        'summary': {
            'total_revenue': sum(day['revenue'] for day in daily_data),
            'total_bookings': sum(day['bookings'] for day in daily_data),
            'avg_occupancy': sum(day['occupancy'] for day in daily_data) / len(daily_data),
            'period_growth': calculate_growth(daily_data)
        },
        'daily_data': daily_data,
        'satisfaction_metrics': [
            {
                'name': 'Overall Experience',
                'icon': 'fa-star',
                'rating': 4.8,
                'reviews': 150,
                'trend': calculate_metric_trend(start_date, end_date, 'experience')
            },
            {
                'name': 'Room Quality',
                'icon': 'fa-bed',
                'rating': 4.6,
                'reviews': 120,
                'trend': calculate_metric_trend(start_date, end_date, 'room_quality')
            },
            {
                'name': 'Service',
                'icon': 'fa-concierge-bell',
                'rating': 4.9,
                'reviews': 140,
                'trend': calculate_metric_trend(start_date, end_date, 'service')
            },
            {
                'name': 'Cleanliness',
                'icon': 'fa-broom',
                'rating': 4.7,
                'reviews': 130,
                'trend': calculate_metric_trend(start_date, end_date, 'cleanliness')
            }
        ],
        'predictions': generate_predictions(end_date),
        'property_data': get_property_data(property_id)
    }

def calculate_growth(data):
    """Calculate period-over-period growth."""
    if len(data) < 2:
        return 0
    
    first_half = sum(day['revenue'] for day in data[:len(data)//2])
    second_half = sum(day['revenue'] for day in data[len(data)//2:])
    
    if first_half == 0:
        return 100
    return ((second_half - first_half) / first_half) * 100

# Mock data generation functions
def generate_revenue_data(date):
    """Generate realistic revenue data based on date patterns."""
    base = 5000
    # Weekend boost
    if date.weekday() >= 5:
        base *= 1.5
    # Season factors
    month = date.month
    if month in [12, 1, 7, 8]:  # Peak seasons
        base *= 1.3
    return round(base * (0.9 + (date.day % 10) / 10))

def generate_booking_data(date):
    """Generate realistic booking numbers."""
    base = 15
    if date.weekday() >= 5:
        base *= 1.4
    return round(base * (0.8 + (date.day % 8) / 10))

def generate_occupancy_data(date):
    """Generate realistic occupancy rates."""
    base = 75
    if date.weekday() >= 5:
        base += 15
    return min(100, round(base * (0.9 + (date.day % 10) / 20)))

def calculate_metric_trend(start_date, end_date, metric):
    """Calculate the trend for a given metric."""
    # Implementation of calculate_metric_trend function
    pass

def get_property_data(property_id):
    """Retrieve property-specific data."""
    # Implementation of get_property_data function
    pass

def generate_predictions(end_date):
    """Generate predictions for the given date."""
    # Implementation of generate_predictions function
    pass

def reviews(request):
    """Handle resort reviews."""
    reviews_data = [
        {
            'guest_name': 'Alice Smith',
            'rating': 5,
            'comment': 'Excellent service and beautiful location!',
            'date': datetime.now() - timedelta(days=2)
        }
    ]
    return render(request, 'dashboard/reviews.html', {'reviews': reviews_data})

def resort_index(request):
    """Resort owner's main dashboard view."""
    context = {
        'revenue': 45850,
        'bookings_count': 24,
        'occupancy_rate': 85,
        'recent_bookings': [
            {
                'guest_name': 'John Doe',
                'room_type': 'Luxury Suite',
                'check_in': timezone.now() + timedelta(days=2),
                'status': 'Confirmed',
                'status_class': 'success'
            },
            {
                'guest_name': 'Sarah Wilson',
                'room_type': 'Ocean View',
                'check_in': timezone.now() + timedelta(days=3),
                'status': 'Pending',
                'status_class': 'warning'
            },
            # Add more booking data as needed
        ]
    }
    return render(request, 'dashboard/resort_index.html', context)

def update_pricing(request):
    """API endpoint to update package pricing."""
    if request.method == 'POST':
        # Add actual pricing update logic here
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def get_analytics_data(request):
    """API endpoint to fetch analytics data."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Add actual analytics data fetching logic here
    data = {
        'revenue': generate_demo_data(),
        'occupancy': generate_demo_data(max_value=100),
        'satisfaction': generate_demo_data(max_value=5)
    }
    
    return JsonResponse(data)

def generate_demo_data(days=30, max_value=50000):
    """Generate demo data for charts."""
    return [random.randint(max_value * 0.7, max_value) for _ in range(days)]

def resort_home(request):
    """Render the resort home page."""
    return render(request, 'dashboard/resort_home.html')

def manage_rooms(request):
    """View for managing rooms."""
    try:
        rooms = Room.objects.all().select_related('category')
        categories = RoomCategory.objects.all()
        
        context = {
            'rooms': rooms,
            'categories': categories,
            'total_rooms': rooms.count(),
            'available_rooms': rooms.filter(status='available').count(),
            'occupied_rooms': rooms.filter(status='occupied').count(),
            'maintenance_rooms': rooms.filter(status='maintenance').count(),
        }
        return render(request, 'dashboard/manage_rooms.html', context)
    except Exception as e:
        messages.error(request, f'Error loading rooms: {str(e)}')
        return redirect('dashboard')

def add_room(request):
    """View for adding a new room."""
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.current_price = room.calculate_price()
            room.save()
            messages.success(request, 'Room added successfully!')
            return redirect('manage_rooms')
    else:
        form = RoomForm()
    return render(request, 'dashboard/room_form.html', {'form': form, 'action': 'Add'})

def edit_room(request, pk):
    """View for editing an existing room."""
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save(commit=False)
            room.current_price = room.calculate_price()
            room.save()
            messages.success(request, 'Room updated successfully!')
            return redirect('manage_rooms')
    else:
        form = RoomForm(instance=room)
    return render(request, 'dashboard/room_form.html', {'form': form, 'action': 'Edit'})

def room_bookings(request, room_id):
    """View for managing room bookings."""
    room = get_object_or_404(Room, id=room_id)
    bookings = RoomBooking.objects.filter(room=room).order_by('-check_in')
    return render(request, 'dashboard/room_bookings.html', {
        'room': room,
        'bookings': bookings
    })

def add_booking(request, room_id):
    """View for adding a new booking."""
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            booking.total_price = room.current_price * (
                (booking.check_out - booking.check_in).days
            )
            booking.save()
            
            # Update room status
            room.status = 'reserved'
            room.save()
            
            messages.success(request, 'Booking added successfully!')
            return redirect('room_bookings', room_id=room.id)
    else:
        form = RoomBookingForm()
    
    return render(request, 'dashboard/booking_form.html', {
        'form': form,
        'room': room,
        'action': 'Add'
    })

def check_availability(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        date = request.POST.get('date')
        
        package = get_object_or_404(Package, pk=package_id)
        check_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        
        is_available = package.is_available(check_date)
        available_sessions = []
        
        if is_available:
            # Get available sessions for the date
            package_activities = PackageActivity.objects.filter(package=package)
            for pa in package_activities:
                booked_sessions = PackageBooking.objects.filter(
                    package=package,
                    booking_date=check_date
                ).values_list('session_time', flat=True)
                
                available_sessions.extend([
                    time for time in pa.session_times
                    if time not in booked_sessions
                ])
        
        return JsonResponse({
            'available': is_available,
            'sessions': available_sessions
        })

def manage_venues(request):
    """View for managing venues."""
    venues = Venue.objects.all()
    total_venues = venues.count()
    available_venues = venues.filter(status='available').count()
    maintenance_venues = venues.filter(status='maintenance').count()
    reserved_venues = venues.filter(status='reserved').count()

    context = {
        'venues': venues,
        'total_venues': total_venues,
        'available_venues': available_venues,
        'maintenance_venues': maintenance_venues,
        'reserved_venues': reserved_venues,
    }
    return render(request, 'dashboard/manage_venues.html', context)

def add_venue(request):
    """View for adding a new venue."""
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue added successfully!')
            return redirect('manage_venues')
    else:
        form = VenueForm()
    return render(request, 'dashboard/venue_form.html', {'form': form, 'action': 'Add'})

def edit_venue(request, pk):
    """View for editing an existing venue."""
    venue = get_object_or_404(Venue, pk=pk)
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue updated successfully!')
            return redirect('manage_venues')
    else:
        form = VenueForm(instance=venue)
    return render(request, 'dashboard/venue_form.html', {'form': form, 'action': 'Edit'})

def venue_bookings(request, venue_id):
    """View for managing venue bookings."""
    venue = get_object_or_404(Venue, id=venue_id)
    bookings = VenueBooking.objects.filter(venue=venue).order_by('-event_date')
    return render(request, 'dashboard/venue_bookings.html', {
        'venue': venue,
        'bookings': bookings
    })

def add_booking(request, venue_id):
    """View for adding a new venue booking."""
    venue = get_object_or_404(Venue, id=venue_id)
    if request.method == 'POST':
        form = VenueBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.venue = venue
            booking.total_price = booking.calculate_price()
            booking.save()
            
            messages.success(request, 'Booking added successfully!')
            return redirect('venue_bookings', venue_id=venue.id)
    else:
        form = VenueBookingForm()
    
    return render(request, 'dashboard/booking_form.html', {
        'form': form,
        'venue': venue,
        'action': 'Add'
    })
