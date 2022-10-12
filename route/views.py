from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import connection
from route import models


# Create your views here.
def route_filter(request, route_type=None, country=None, location=None):
    cursor = connection.cursor()
    query_filter = []

    if route_type is not None:
        query_filter.append(f"route_type='{route_type}'")
    if country is not None:
        query_filter.append(f"country='{country}'")
    if location is not None:
        query_filter.append(f"location='{location}'")

    filter_string = ' and '.join(query_filter)

    joining = """SELECT route_route.country,
       route_route.destination,
       route_route.duration,
       route_route.stopping_point,
       route_route.route_type,
       start_point.name,
       end_point.name
    FROM route_route
    JOIN route_places as start_point
        ON start_point.id = route_route.starting_point

    JOIN route_places as end_point
        ON end_point.id = route_route.destination
    WHERE """ + filter_string

    cursor.execute(joining)
    result = cursor.fetchall()

    new_result = [{'country': itm[0], 'description': itm[1], 'duration': itm[2], "stopping": itm[3],
                   'type': itm[4], 'start': itm[5], 'end': itm[6]} for itm in result]

    return HttpResponse(new_result)


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
    if request.user.has_perm('route.add_route'):
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
                                     location=location, description=description, route_type=route_type,
                                     duration=duration,
                                     stopping_point={})

            new_route.save()

            return HttpResponse('Created new route!')

    else:
        return HttpResponse('Not allowed to add route')


def route_add_event(request, route_id):
    if request.user.has_perm('route.add_event'):
        if request.method == 'GET':
            return render(request, 'add_event.html')
        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            price = request.POST.get('price')

            new_event = models.Event(id_route=route_id, start_date=start_date, price=price, event_admin=1,
                                     approve_user=[],
                                     pending_users=[])
            new_event.save()

            return HttpResponse('Created new event')

    else:
        return HttpResponse('Not allowed to add event')


def event_handler(request, event_id):
    event_info = models.Event.objects.all().filter(id=event_id)
    return HttpResponse([{'id': itm.id, 'id_route': itm.id_route, 'event_admin': itm.event_admin,
                          'approve_user': itm.approve_user, 'pending_users': itm.pending_users,
                          'start_date': itm.start_date, 'price': itm.price} for itm in event_info])


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'login.html')
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponse('User is login')
            else:
                return HttpResponse('No user')
    else:
        return HttpResponse('<a href="logout" > logout</a>')


def user_registration(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'registration.html')
        if request.method == 'POST':
            user = User.objects.create_user(username=request.POST.get('username'),
                                            password=request.POST.get('password'),
                                            email=request.POST.get('email'),
                                            first_name=request.POST.get('first_name'),
                                            last_name=request.POST.get('last_name'))
            user.save()
            return HttpResponse('Created user')
    else:
        return HttpResponse('<a href="logout" > logout</a>')


def logout_user(request):
    logout(request)
    return redirect('/login')
