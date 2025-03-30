from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Passenger, Ticket, Berth, RACTicket, Waitlist
from .serializers import TicketSerializer
from django.shortcuts import render
from django.apps import AppConfig
from django.db.utils import IntegrityError
from django.db.models import Count

def index(request):
    return render(request, "index.html")


class BookedTickets(APIView):
    def get(self, request):
        tickets = Ticket.objects.select_related("passenger").all()
        data = [
            {
                "ticket_id": ticket.id,
                "passenger_name": ticket.passenger.name,
                "age": ticket.passenger.age,
                "gender": ticket.passenger.gender,
                "status": ticket.status,
                "berth_type": ticket.berth_type,
            }
            for ticket in tickets
        ]
        return Response(data, status=status.HTTP_200_OK)


# def create_initial_berths():
#     print("Initializing Berths...")
#     for i in range(22):
#         Berth.objects.create(berth_type="lower", occupied=False)
#     for i in range(21):
#         Berth.objects.create(berth_type="middle", occupied=False)
#     for i in range(10):
#         Berth.objects.create(berth_type="upper", occupied=False)
#     for i in range(5):
#         Berth.objects.create(berth_type="side-upper", occupied=False)
#     for i in range(9):
#         rac_berth = Berth.objects.create(berth_type="side-lower", occupied=False)
#         RACTicket.objects.create(berth=rac_berth, occupied=False)
#         RACTicket.objects.create(berth=rac_berth, occupied=False)
#     print("Berths Initialized")
# create_initial_berths()  # Call the function to create initial berths


# #delete data of all models
# Ticket.objects.all().delete()
# Berth.objects.all().update(occupied=False, ticket=None)
# Berth.objects.all().delete()
# RACTicket.objects.all().update(occupied=False, passenger=None)
# Waitlist.objects.all().delete()
# Passenger.objects.all().delete()

# # print("All data deleted!")


print("Total Berths:", Berth.objects.count())
print("Unoccupied Berths:", Berth.objects.filter(occupied=False).count())
print("Total RAC Slots:", RACTicket.objects.count())
print("Unoccupied RAC Slots:", RACTicket.objects.filter(occupied=False).count())
print("Total RAC Slots Used:", Ticket.objects.filter(status="rac").count())


BERTH_LIMITS = {
    "lower": 22, 
    "middle": 21,
    "upper": 10,
    "side-upper": 5,
    "side-lower": 5
}

class BookTicket(APIView):
    def post(self, request):
        print("\nIncoming Request:", request.data)
        with transaction.atomic():
            passenger_data = request.data.get("passenger")
            if not passenger_data:
                return Response({"message": "Missing passenger data"}, status=status.HTTP_400_BAD_REQUEST)

            passenger_data["age"] = int(passenger_data["age"])
            passenger = Passenger.objects.create(**passenger_data)

            print(f"Passenger Created: {passenger.name} | Age: {passenger.age} | Gender: {passenger.gender}")

            if self.has_available_confirmed_berth():
                print("Confirmed berth available")
                berth = self.get_available_berth(passenger)
                if berth:
                    print(f"Allocating Confirmed Berth: {berth.berth_type}")
                    return self.allocate_confirmed_ticket(passenger, berth)

            print("No confirmed berths left")

            if self.has_available_rac_slot():
                print("RAC slot available")
                return self.allocate_rac_ticket(passenger)

            print("No RAC slots available")

            if self.has_available_waitlist():
                print("Waitlist slot available")
                return self.allocate_waitlist_ticket(passenger)

            print("No tickets available")
            return Response({"message": "No tickets available"}, status=status.HTTP_400_BAD_REQUEST)

    def has_available_confirmed_berth(self):
        total_confirmed_tickets = Ticket.objects.filter(status="confirmed").count()
        return total_confirmed_tickets < sum(BERTH_LIMITS.values())

    def get_available_berth(self, passenger):
        """
        Allocates an appropriate berth based on passenger priority and berth availability.
        """
        print("\nChecking Available Berths:")
        for berth_type in BERTH_LIMITS.keys():
            count = Ticket.objects.filter(status="confirmed", berth_type=berth_type).count()
            print(f"  🔹 {berth_type}: {count}/{BERTH_LIMITS[berth_type]} occupied")

        berth_priority_order = ["lower", "middle", "upper", "side-upper", "side-lower"]

        # 🔹 Prioritize "lower" berth for senior citizens & women with children
        if passenger.age >= 60 or (passenger.gender.lower() == "female" and passenger.child_under_5):
            lower_berth = Berth.objects.filter(berth_type="lower", occupied=False).first()
            if lower_berth:  # Check if at least one lower berth is available
                print(f"Allocating Lower Berth (Priority) to {passenger.name}")
                return lower_berth
            print("No Lower Berths Left for Priority Passengers")

        # 🔹 Otherwise, check available berths in priority order
        for berth_type in berth_priority_order:
            occupied_count = Ticket.objects.filter(status="confirmed", berth_type=berth_type).count()
            if occupied_count < BERTH_LIMITS[berth_type]:  # Check berth limits
                berth = Berth.objects.filter(berth_type=berth_type, occupied=False).first()
                if berth:
                    print(f"Allocating Available Berth: {berth.berth_type}")
                    return berth

        print("No Available Berths Found")
        return None  # No available berth

    def has_available_rac_slot(self):
        rac_count = Ticket.objects.filter(status="rac").count()
        print(f"Checking RAC Slots: {rac_count}/18 occupied")
        return rac_count < 18  # Ensure correct condition

    def has_available_waitlist(self):
        return Waitlist.objects.count() < 10

    def allocate_confirmed_ticket(self, passenger, berth):
        with transaction.atomic():
            berth = Berth.objects.select_for_update().get(id=berth.id)

            if berth.occupied:
                return Response({"message": "This berth was just booked, please try again"}, status=status.HTTP_400_BAD_REQUEST)

            ticket = Ticket.objects.create(passenger=passenger, status="confirmed", berth_type=berth.berth_type)
            berth.occupied = True
            berth.ticket = ticket
            berth.save()

            print(f"Confirmed Ticket Created: {ticket.id} | Berth Type: {ticket.berth_type}")
            return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    def allocate_rac_ticket(self, passenger):
        with transaction.atomic():
            rac_berth = RACTicket.objects.filter(occupied=False).first()
            if not rac_berth:
                return Response({"message": "RAC is full"}, status=status.HTTP_400_BAD_REQUEST)

            rac_passenger_count = Ticket.objects.filter(status="rac", berth_type="side-lower").count()
            if rac_passenger_count == 1:
                rac_berth.occupied = True
            rac_berth.passenger = passenger
            rac_berth.save()

            ticket = Ticket.objects.create(passenger=passenger, status="rac", berth_type="side-lower")
            print(f"RAC Ticket Created: {ticket.id} | Berth Type: {ticket.berth_type}")

            return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)
        
    def allocate_waitlist_ticket(self, passenger):
        with transaction.atomic():
            waitlist_position = Waitlist.objects.count() + 1
            Waitlist.objects.create(passenger=passenger, position=waitlist_position)

            print(f"Passenger {passenger.name} added to waitlist at position {waitlist_position}")
            return Response(
                {"message": "Added to waiting list", "waitlist_position": waitlist_position},
                status=status.HTTP_202_ACCEPTED,
            )
        

class CancelTicket(APIView):
    def post(self, request, ticket_id):
        with transaction.atomic():
            print("Ticket",ticket_id)
            try:
                ticket = Ticket.objects.get(id=ticket_id)
            except Ticket.DoesNotExist:
                return Response({"message": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

            if ticket.status == "confirmed":
                berth = Berth.objects.get(ticket=ticket)
                berth.occupied = False
                berth.ticket = None
                berth.save()
                ticket.delete()

                rac_ticket = Ticket.objects.filter(status="rac").order_by("created_at").first()
                if rac_ticket:
                    berth.ticket = rac_ticket
                    berth.occupied = True
                    berth.save()
                    rac_ticket.status = "confirmed"
                    rac_ticket.save()
                    RACTicket.objects.filter(passenger=rac_ticket.passenger).delete()

                    waitlist_ticket = Waitlist.objects.order_by("created_at").first()
                    if waitlist_ticket:
                        BookTicket().allocate_rac_ticket(waitlist_ticket.passenger)  # Directly call method
                        waitlist_ticket.delete()

            elif ticket.status == "rac":
                RACTicket.objects.filter(passenger=ticket.passenger).delete()
                ticket.delete()
                waitlist_ticket = Waitlist.objects.order_by("created_at").first()
                if waitlist_ticket:
                    BookTicket().allocate_rac_ticket(waitlist_ticket.passenger)
                    waitlist_ticket.delete()

            elif ticket.status == "waiting":
                Waitlist.objects.filter(passenger=ticket.passenger).delete()
                ticket.delete()

            return Response({"message": "Ticket canceled successfully"}, status=status.HTTP_200_OK)


class AvailableTickets(APIView):
    def get(self, request):
        confirmed_available = 63 - Ticket.objects.filter(status="confirmed").count()
        rac_available = 18 - Ticket.objects.filter(status="rac").count()
        waitlist_available = 10 - Waitlist.objects.count()

        return Response(
            {
                "confirmed_berths_available": confirmed_available,
                "rac_slots_available": rac_available,
                "waitlist_slots_available": waitlist_available,
            },
            status=status.HTTP_200_OK,
        )