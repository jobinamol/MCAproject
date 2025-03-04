from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

# Create your models here.

class Activity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    max_participants = models.IntegerField(default=1)
    
    def __str__(self):
        return self.name

class Package(models.Model):
    PACKAGE_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('seasonal', 'Seasonal'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)  # e.g., "3 days", "1 week"
    image = models.ImageField(upload_to='package_images/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=PACKAGE_STATUS, default='active')
    
    # New fields for availability and limits
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    daily_limit = models.IntegerField(default=0, help_text="0 for unlimited")
    total_limit = models.IntegerField(default=0, help_text="0 for unlimited")
    current_bookings = models.IntegerField(default=0)
    activities = models.ManyToManyField(Activity, through='PackageActivity')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_available(self, date=None):
        if not date:
            date = timezone.now().date()
        
        # Check if package is active
        if self.status != 'active':
            return False
            
        # Check date range if specified
        if self.start_date and self.end_date:
            if not (self.start_date <= date <= self.end_date):
                return False
        
        # Check total limit
        if self.total_limit > 0 and self.current_bookings >= self.total_limit:
            return False
            
        # Check daily limit
        if self.daily_limit > 0:
            daily_bookings = PackageBooking.objects.filter(
                package=self,
                booking_date=date
            ).count()
            if daily_bookings >= self.daily_limit:
                return False
                
        return True

class PackageActivity(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    session_times = models.JSONField(default=list, help_text="List of available time slots")
    
    class Meta:
        unique_together = ['package', 'activity']

class PackageBooking(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    booking_date = models.DateField()
    session_time = models.TimeField()
    participant_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class RoomCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.JSONField(default=list)

    def __str__(self):
        return self.name

class Room(models.Model):
    ROOM_STATUS = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('reserved', 'Reserved'),
    )

    number = models.CharField(max_length=10, unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.PROTECT)
    floor = models.IntegerField()
    capacity = models.IntegerField(default=2)
    size = models.IntegerField(help_text="Size in square meters")
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='available')
    is_active = models.BooleanField(default=True)
    
    # Dynamic pricing fields
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_multiplier = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    def __str__(self):
        return f"Room {self.number}"

    def calculate_price(self, date=None):
        base = self.category.base_price
        return base * self.price_multiplier

class RoomBooking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(
        max_length=20,
        choices=[
            ('confirmed', 'Confirmed'),
            ('checked_in', 'Checked In'),
            ('checked_out', 'Checked Out'),
            ('cancelled', 'Cancelled'),
        ],
        default='confirmed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking for Room {self.room.number}"

class Venue(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.IntegerField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.JSONField(default=list)
    image = models.ImageField(upload_to='venue_images/', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('maintenance', 'Under Maintenance'),
            ('reserved', 'Reserved'),
        ],
        default='available'
    )

    def __str__(self):
        return self.name

class EventType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    setup_time = models.IntegerField(help_text="Setup time in minutes")
    cleanup_time = models.IntegerField(help_text="Cleanup time in minutes")
    
    def __str__(self):
        return self.name

class VenueBooking(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    guest_count = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event_type} at {self.venue} on {self.event_date}"

    def calculate_price(self):
        duration_hours = (
            self.end_time.hour - self.start_time.hour + 
            (self.end_time.minute - self.start_time.minute) / 60
        )
        return (self.venue.price_per_hour * duration_hours) + self.event_type.base_price
