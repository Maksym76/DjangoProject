from django.shortcuts import render
from django.http import HttpResponse
from route import models


# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    query_filter = {}

    if route_type is not None:
        query_filter['route_type'] = route_type
    if country is not None:
        query_filter['country'] = country
    if location is not None:
        query_filter['location'] = location

    result = models.Route.objects.all().filter(**query_filter)
    return HttpResponse([{'starting_point': itm.starting_point, 'stopping_point': itm.stopping_point,
                          'destination': itm.destination, 'country': itm.country, 'location': itm.location,
                          'description': itm.description, 'route_type': itm.route_type, 'duration': itm.duration}
                         for itm in result])


def route_datail(request, route_id):
    result = models.Route.objects.all().filter(id=route_id)
    return HttpResponse([{'starting_point': itm.starting_point, 'stopping_point': itm.stopping_point,
                          'destination': itm.destination, 'country': itm.country, 'location': itm.location,
                          'description': itm.description, 'route_type': itm.route_type, 'duration': itm.duration}
                         for itm in result])


def route_review(request, route_id):
    result = models.Review.objects.all().filter(route_id=route_id)
    return HttpResponse([{'route_id': itm.route_id, 'review_text': itm.review_text, 'review_rate': itm.review_rate}
                         for itm in result])


def route_add(request):
    if request.method == 'GET':
        return render(request, 'add_route.html')
    if request.method == 'POST':
        starting_point = request.POST.get('starting_point')
        destination = request.POST.get('destination')
        country = request.POST.get('country')
        location = request.POST.get('location')
        description = request.POST.get('description')
        route_type = request.POST.get('route_type')
        duration = request.POST.get('duration')

        start_obj = models.Places.objects.get(name=starting_point)
        destination_obj = models.Places.objects.get(name=destination)

        new_route = models.Route(starting_point=start_obj.id, destination=destination_obj.id, country=country,
                                 location=location, description=description, route_type=route_type, duration=duration,
                                 stopping_point={})

        new_route.save()

    return HttpResponse('Created new route!')


def route_add_event(request, route_id):
    if request.method == 'GET':
        return render(request, 'add_event.html')
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        price = request.POST.get('price')

        new_event = models.Event(id_route=route_id, start_date=start_date, price=price, event_admin=1, approve_user=[],
                                 pending_users=[])
        new_event.save()

    return HttpResponse('Created new event')


def event_handler(request, event_id):
    event_info = models.Event.objects.all().filter(id=event_id)
    return HttpResponse([{'id': itm.id, 'id_route': itm.id_route, 'event_admin': itm.event_admin,
                          'approve_user': itm.approve_user, 'pending_users': itm.pending_users,
                          'start_date': itm.start_date, 'price': itm.price} for itm in event_info])
