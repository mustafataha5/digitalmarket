from django.core.management.base import BaseCommand
from main.models import Category

class Command(BaseCommand):
    help = 'Seed initial product categories'

    def handle(self, *args, **kwargs):
        categories = [
            "Electronics",
            "Clothing",
            "Books",
            "Home & Kitchen",
            "Sports & Outdoors",
            "Health & Beauty",
            "Toys & Games",
            "Automotive"
        ]

        for name in categories:
            category, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {name}'))
