from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from tracker.models import Ticket


@shared_task(bind=True)
def send_mail_about_tomorrow_flight(self):
    tickets = Ticket.objects.all()
    current_datetime = timezone.now()
    tomorrow_datetime = current_datetime + timedelta(days=1)
    for ticket in tickets:
        mail_subject = "Notification about tomorrow flight"
        message = (
            "Hello, dear customer!\n"
            f"Your flight from {ticket.flight.route.source.name}"
            f" to {ticket.flight.route.destination.name} will"
            f"depart tomorrow at {ticket.flight.departure_time}"
        )
        to_email = ticket.order.user.email
        if ticket.flight.departure_time.date() == tomorrow_datetime.date():
            send_mail(
                subject=mail_subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[to_email],
                fail_silently=True,
            )
    return "Done"
