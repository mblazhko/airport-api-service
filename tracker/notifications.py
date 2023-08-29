from django.conf import settings
from django.core.mail import send_mail


def send_order_confirmation_email(order):
    subject = "Order Confirmation"
    message = (
        f"Your order is successfully created!\n "
        f"Information about tickets:\n "
    )

    for ticket in order.tickets.all():
        message += (
            f"Passenger: {ticket.full_name}\n"
            f"Seat: {ticket.seat}\n"
            f"Flight: {ticket.flight}\n"
            f"Departure Time: {ticket.flight.departure_time}\n\n"
        )

    from_email = settings.EMAIL_HOST_USER
    recipient_list = [order.user.email]

    send_mail(
        subject, message, from_email, recipient_list, fail_silently=False
    )
