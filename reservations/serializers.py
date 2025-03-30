from rest_framework import serializers
from .models import Passenger, Ticket, Berth

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer()
    class Meta:
        model = Ticket
        fields = '__all__'