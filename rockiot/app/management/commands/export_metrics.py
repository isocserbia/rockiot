from django.core.management.base import BaseCommand

from app.system.metrics import MetricsExporter


class Command(BaseCommand):
    def handle(self, **options):
        exporter = MetricsExporter()
        exporter.start()
        print("Started metrics exporter thread")
