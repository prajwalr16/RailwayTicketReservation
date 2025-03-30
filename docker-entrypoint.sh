#!/bin/sh

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser (if it doesn’t exist)
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
from reservations.models import Berth, RACTicket, Ticket, Passenger, Waitlist
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "admin")
Ticket.objects.all().delete()
Berth.objects.all().update(occupied=False, ticket=None)
Berth.objects.all().delete()
RACTicket.objects.all().update(occupied=False, passenger=None)
Waitlist.objects.all().delete()
Passenger.objects.all().delete()
if not Berth.objects.exists():  # Prevent duplicate creation
    for i in range(22):
        Berth.objects.create(berth_type="lower", occupied=False)
    for i in range(21):
        Berth.objects.create(berth_type="middle", occupied=False)
    for i in range(10):
        Berth.objects.create(berth_type="upper", occupied=False)
    for i in range(5):
        Berth.objects.create(berth_type="side-upper", occupied=False)
    for i in range(9):
        rac_berth = Berth.objects.create(berth_type="side-lower", occupied=False)
        RACTicket.objects.create(berth=rac_berth, occupied=False)
        RACTicket.objects.create(berth=rac_berth, occupied=False)

EOF

# Collect static files
python manage.py collectstatic --noinput

# Start the server
exec "$@"
