from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from mongo_utils import MongoDBConnection
from django.http import HttpResponse
from django.db import connection
from bson import ObjectId
from route import models
import json


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
        ON end_point.id = route_route.starting_point
    WHERE """ + filter_string

    cursor.execute(joining)
    result = cursor.fetchall()

    new_result = [{'country': itm[0], 'description': itm[1], 'duration': itm[2], "stopping": itm[3],
                   'type': itm[4], 'start': itm[5], 'end': itm[6]} for itm in result]

    return HttpResponse(new_result)


def route_datail(request, route_id):
    cursor = connection.cursor()

    sql_query = f"""SElECT route_route.id,
    start.name as starting_point,
    route_route.stopping_point,
    route_route.destination,
    route_route.country,
    route_route.location,
    route_route.description,
    route_route.route_type,
    route_route.duration
    FROM route_route
    JOIN route_places as start
        ON start.id = route_route.starting_point
    WHERE route_route.id = {route_id}"""

    cursor.execute(sql_query)
    result = cursor.fetchall()

    new_result = [{'route_id': itm[0], 'starting_point': itm[1], 'stopping_point': itm[2], "destination": itm[3],
                   'country': itm[4], 'location': itm[5], 'description': itm[6], 'route_type': itm[7],
                   'duration': itm[8]} for itm in result]

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collect = db['stop_points']
        stop_point = collect.find_one({'_id': ObjectId(new_result[0]['stopping_point'])})

    return HttpResponse([new_result, stop_point])

    # result = models.Route.objects.all().filter(id=route_id)
    # return HttpResponse([{'starting_point': itm.starting_point, 'stopping_point': itm.stopping_point,
    #                       'destination': itm.destination, 'country': itm.country, 'location': itm.location,
    #                       'description': itm.description, 'route_type': itm.route_type, 'duration': itm.duration}
    #                      for itm in result])


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
            stopping_point = request.POST.get('stopping_point')
            destination = request.POST.get('destination')
            country = request.POST.get('country')
            location = request.POST.get('location')
            description = request.POST.get('description')
            route_type = request.POST.get('route_type')
            duration = request.POST.get('duration')

            stop_list = json.loads(stopping_point)

            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                collect = db['stop_points']
                id_stop_point = collect.insert_one({'points': stop_list}).inserted_id

            start_obj = models.Places.objects.get(name=starting_point)
            destination_obj = models.Places.objects.get(name=destination)

            new_route = models.Route(starting_point=start_obj.id, destination=destination_obj.id, country=country,
                                     location=location, description=description, route_type=route_type,
                                     duration=duration,
                                     stopping_point=id_stop_point)

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
    cursor = connection.cursor()

    sql_query = f"""SELECT route_event.id,
    route_event.id_route,
    route_event.start_date,
    route_event.price,
    route_event.event_user,
    start.name as starting_point,
    route_route.stopping_point as stopping_point
    FROM route_event, route_route
    JOIN route_places as start
        ON start.id = route_route.starting_point
    WHERE route_event.id = {event_id}
    LIMIT 1"""

    cursor.execute(sql_query)
    result = cursor.fetchall()

    new_result = [{'event_id': itm[0], 'id_route': itm[1], 'start_date': itm[2], "price": itm[3],
                   'id_event_user': itm[4], 'starting_point': itm[5], 'stopping_point': itm[6]} for itm in result]

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        collect = db['event_user']
        event_user = collect.find_one({'_id': ObjectId(new_result[0]['id_event_user'])})

    users_pending = User.objects.filter(pk__in=event_user['pending'])
    users_approved = User.objects.filter(pk__in=event_user['approved'])

    list_users_pending = [{itm.id: itm.username} for itm in users_pending]
    list_users_approved = [{itm.id: itm.username} for itm in users_approved]

    new_result[0]['users_pending'] = list_users_pending
    new_result[0]['users_approved'] = list_users_approved

    return HttpResponse(new_result)

    # event_info = models.Event.objects.all().filter(id=event_id)
    # return HttpResponse([{'id': itm.id, 'id_route': itm.id_route, 'event_admin': itm.event_admin,
    #                       'approve_user': itm.approve_user, 'pending_users': itm.pending_users,
    #                       'start_date': itm.start_date, 'price': itm.price} for itm in event_info])


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


def add_me_to_event(request, event_id):
    user = request.user.id
    event = models.Event.objects.filter(id=event_id).first()

    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        event_users = db["event_user"]
        all_event_users = event_users.find_one({'_id': ObjectId(event.event_user)})

        if user in all_event_users['pending'] or user in all_event_users['approved']:
            return HttpResponse('You are in pending users')

        else:
            all_event_users['pending'].append(user)
            event_users.update_one({'_id': ObjectId(event.event_user)}, {"$set": all_event_users}, upsert=False)

    return redirect("route:event_info", *event_id)


def event_approved_user(request, event_id):
    if request.method == "GET":
        if request.user.is_superuser:
            event = models.Event.objects.filter(id=event_id).first()

            with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
                event_users = db['event_user']
                all_event_users = event_users.find_one({'_id': ObjectId(event.event_user)})
                pending_users = all_event_users.get('pending')
                context = {"pending_users": pending_users}
            return render(request, "approved_user.html", context=context)

        else:
            return HttpResponse("You don't have access")

    if request.method == "POST":
        event = models.Event.objects.filter(id=event_id).first()
        approved_user = int(request.POST.get("user id"))

        with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
            event_users = db['event_user']
            all_event_users = event_users.find_one({'_id': ObjectId(event.event_user)})

            if approved_user in all_event_users["pending"]:
                all_event_users["pending"].remove(approved_user)
                all_event_users["approved"].append(approved_user)
                event_users.update_one({'_id': ObjectId(event.event_user)}, {"$set": all_event_users}, upsert=False)

            else:
                return HttpResponse("""User with this id is not in the pending list <br>
                <a href="approved_user" >approved user</a>""")

        return HttpResponse("""User is accepted <br>
        <a href="approved_user" >approved user</a>""")
