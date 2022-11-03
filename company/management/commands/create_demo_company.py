from django.core.management.base import BaseCommand
import random
from company.models import Company

class Command(BaseCommand):
    def handle(self, *args, **options):

        for i in range(1,500):
            dot = random.randint(1*i, 500*i)
            legal_name = f'Legal_{dot}'
            name = f'name_{dot}'
            c = Company.objects.create(name=name, legal_name=legal_name, dot=dot)
            try:
                c.save()
            except:
                continue