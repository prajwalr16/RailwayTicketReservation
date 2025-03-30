from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", index, name="index"),
    path("api/v1/tickets/book", BookTicket.as_view(), name="book-ticket"),
    path("api/v1/tickets/booked", BookedTickets.as_view(), name="book-ticket"),
    path("api/v1/tickets/cancel/<int:ticket_id>/", CancelTicket.as_view(), name="cancel-ticket"),
    path("api/v1/tickets/available", AvailableTickets.as_view(), name="available-tickets"),
]

# Serve static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)