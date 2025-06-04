from django.core.management.base import BaseCommand
from main.models import Product, Category

class Command(BaseCommand):
    help = 'Seed initial products'

    def handle(self, *args, **kwargs):
        data = [
            ("Smartphone", "Latest Android smartphone", 699.99, "uploads/smartphone.jpg", "Electronics"),
            ("Python Book", "Learn Python programming", 29.99, "uploads/python_book.jpg", "Books"),
            ("T-Shirt", "Comfortable cotton t-shirt", 15.00, "uploads/tshirt.jpg", "Clothing"),
        ]

        for name, desc, price, file_path, cat_name in data:
            try:
                category = Category.objects.get(name=cat_name)
                Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'desc': desc,
                        'price': price,
                        'file': file_path,
                        'category': category
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Added: {name}'))
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Category {cat_name} not found!'))
