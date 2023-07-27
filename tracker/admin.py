from django.contrib import admin

from tracker.models import Airport, Crew, Country, City, Route, AirplaneType, \
    Airplane, Order, Flight, Ticket, Passenger

admin.site.register(Crew)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Order)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(Passenger)
