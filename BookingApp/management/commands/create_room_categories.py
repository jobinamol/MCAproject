from django.core.management.base import BaseCommand
from BookingApp.models import RoomCategory

class Command(BaseCommand):
    help = 'Create initial room categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'Standard Room',
                'description': 'Comfortable room with basic amenities',
                'base_price': 199.99,
                'amenities': ['Wi-Fi', 'TV', 'Air Conditioning', 'Private Bathroom']
            },
            {
                'name': 'Deluxe Room',
                'description': 'Spacious room with premium amenities',
                'base_price': 299.99,
                'amenities': ['Wi-Fi', 'Smart TV', 'Mini Bar', 'Ocean View', 'King Bed']
            },
            {
                'name': 'Suite',
                'description': 'Luxury suite with separate living area',
                'base_price': 499.99,
                'amenities': ['Wi-Fi', 'Smart TV', 'Mini Bar', 'Ocean View', 'Kitchen', 'Living Room']
            }
        ]

        for category_data in categories:
            RoomCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully created room categories')) 