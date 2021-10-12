import os, django
from app.models import Device
from django.contrib.auth.models import User
from app.rabbitops.amqp_consumer import ReconnectingRabbitPikaTaskConsumer
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        consumer = ReconnectingRabbitPikaTaskConsumer()
        # consumer.daemon = True
        consumer.start()
        print("Started rabbit pika consumer thread [name: %s]" % consumer.getName())