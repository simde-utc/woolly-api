from django.core.management.base import BaseCommand
from core.faker import FakeModelFactory

class FakeSeeder(BaseCommand):
    help = "Seed fake models into the database."

    def add_arguments(self, parser):
        parser.add_argument('sample', nargs='+')
        parser.add_argument('full_sale',
                            action='store_true',
                            default=True,
                            help='Create a full sale')

    def handle(self, *args, **options):
        raise NotImplementedError()
