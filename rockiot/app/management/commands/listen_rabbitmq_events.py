from django.core.management.base import BaseCommand

from app.rabbitops.events_consumer import ReconnectingRabbitPikaEventConsumer


class Command(BaseCommand):
    def handle(self, **options):
        consumer = ReconnectingRabbitPikaEventConsumer()
        consumer.start()
        print("Started rabbitmq events consumer thread [name: %s]" % consumer.getName())
