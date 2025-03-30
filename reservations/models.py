from django.db import models, transaction
from django.utils.timezone import now

# Create your models here.

class Passenger(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    child_under_5 = models.BooleanField(default=False)

class Ticket(models.Model):
    STATUS_CHOICES = [('confirmed', 'Confirmed'), ('rac', 'RAC'), ('waiting', 'Waiting List')]
    passenger = models.OneToOneField(Passenger, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    berth_type = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Berth(models.Model):
    BERTH_TYPES = [('lower', 'Lower'), ('middle', 'Middle'), ('upper', 'Upper'), ('side-lower', 'Side Lower'), ('side-upper', 'Side Upper')]
    berth_type = models.CharField(max_length=20, choices=BERTH_TYPES)
    occupied = models.BooleanField(default=False)
    ticket = models.OneToOneField(Ticket, null=True, blank=True, on_delete=models.SET_NULL)

class RACTicket(models.Model):
    berth = models.ForeignKey(Berth, on_delete=models.CASCADE, default=1)
    passenger = models.OneToOneField(Passenger, on_delete=models.CASCADE, null=True, blank=True)
    occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)

class Waitlist(models.Model):
    passenger = models.OneToOneField(Passenger, on_delete=models.CASCADE)
    position = models.IntegerField(unique=True)
    created_at = models.DateTimeField(default=now)