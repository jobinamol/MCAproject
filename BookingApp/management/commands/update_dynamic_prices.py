from django.core.management.base import BaseCommand
from django.utils import timezone
from BookingApp.models import Room, Package, Venue
from BookingApp.services.pricing_service import DynamicPricingService

class Command(BaseCommand):
    help = 'Update prices based on dynamic pricing analysis'

    def handle(self, *args, **options):
        pricing_service = DynamicPricingService()
        today = timezone.now().date()

        # Update Room prices
        for room in Room.objects.filter(is_active=True):
            multiplier = pricing_service.calculate_price_multiplier(
                'room', room.id, today
            )
            room.current_price = room.category.base_price * multiplier
            room.price_multiplier = multiplier
            room.save()

        # Update Package prices
        for package in Package.objects.filter(status='active'):
            multiplier = pricing_service.calculate_price_multiplier(
                'package', package.id, today
            )
            package.price = package.base_price * multiplier
            package.save()

        # Update Venue prices
        for venue in Venue.objects.filter(status='available'):
            multiplier = pricing_service.calculate_price_multiplier(
                'venue', venue.id, today
            )
            venue.price_per_hour = venue.base_price_per_hour * multiplier
            venue.save()

        self.stdout.write(
            self.style.SUCCESS('Successfully updated dynamic prices')
        ) 