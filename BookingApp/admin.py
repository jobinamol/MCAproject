from django.contrib import admin
from .models import Activity, Package, PackageActivity, PackageBooking

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'max_participants')
    search_fields = ('name',)

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'status', 'daily_limit', 'total_limit', 'current_bookings')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('name',)

@admin.register(PackageActivity)
class PackageActivityAdmin(admin.ModelAdmin):
    list_display = ('package', 'activity')
    list_filter = ('package', 'activity')

@admin.register(PackageBooking)
class PackageBookingAdmin(admin.ModelAdmin):
    list_display = ('package', 'booking_date', 'session_time', 'participant_count')
    list_filter = ('booking_date', 'package')
    search_fields = ('package__name',)
