from django import forms
from django.forms import inlineformset_factory
from .models import Package, Activity, PackageActivity, Room, RoomCategory, RoomBooking, Venue, EventType, VenueBooking
from django.utils import timezone

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = [
            'name', 'description', 'price', 'duration', 'image', 'status',
            'start_date', 'end_date', 'daily_limit', 'total_limit'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'description', 'duration', 'max_participants']

class PackageActivityForm(forms.ModelForm):
    session_times = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter time slots in HH:MM format, one per line"
    )

    class Meta:
        model = PackageActivity
        fields = ['activity', 'session_times']

    def clean_session_times(self):
        times = self.cleaned_data['session_times'].split('\n')
        cleaned_times = []
        for time in times:
            time = time.strip()
            if time:
                try:
                    # Validate time format
                    hours, minutes = map(int, time.split(':'))
                    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                        raise forms.ValidationError(f"Invalid time format: {time}")
                    cleaned_times.append(f"{hours:02d}:{minutes:02d}")
                except ValueError:
                    raise forms.ValidationError(f"Invalid time format: {time}")
        return cleaned_times

# Create the Activity Formset
ActivityFormSet = inlineformset_factory(
    Package,
    PackageActivity,
    fields=['activity', 'session_times'],
    extra=1,
    can_delete=True,
    widgets={
        'session_times': forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Enter times (HH:MM), one per line\nExample:\n09:00\n14:00'
        })
    }
)

class RoomCategoryForm(forms.ModelForm):
    class Meta:
        model = RoomCategory
        fields = ['name', 'description', 'base_price', 'amenities']
        widgets = {
            'amenities': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter amenities, one per line'
            })
        }

    def clean_amenities(self):
        amenities = self.cleaned_data['amenities'].split('\n')
        return [amenity.strip() for amenity in amenities if amenity.strip()]

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'number', 'category', 'floor', 'capacity', 
            'size', 'status', 'is_active', 'price_multiplier'
        ]

class RoomBookingForm(forms.ModelForm):
    class Meta:
        model = RoomBooking
        fields = [
            'guest_name', 'guest_email', 'guest_phone',
            'check_in', 'check_out', 'adults', 'children'
        ]
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'description', 'capacity', 'price_per_hour', 'amenities', 'image', 'status']
        widgets = {
            'amenities': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter amenities, one per line'
            })
        }

    def clean_amenities(self):
        amenities = self.cleaned_data['amenities'].split('\n')
        return [amenity.strip() for amenity in amenities if amenity.strip()]

class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ['name', 'description', 'base_price', 'setup_time', 'cleanup_time']

class VenueBookingForm(forms.ModelForm):
    class Meta:
        model = VenueBooking
        fields = [
            'event_type', 'customer_name', 'customer_email', 'customer_phone',
            'event_date', 'start_time', 'end_time', 'guest_count', 'special_requests'
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        event_date = cleaned_data.get('event_date')
        venue = self.instance.venue if self.instance else None

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time")

        if event_date and event_date < timezone.now().date():
            raise forms.ValidationError("Event date cannot be in the past")

        return cleaned_data 