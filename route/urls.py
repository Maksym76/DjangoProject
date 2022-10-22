from . import views
from django.urls import path

app_name = "route"
urlpatterns = [
    path('', views.route_filter, name='index'),
    path('<int:route_id>', views.route_datail, name='route_info'),
    path('<int:route_id>/review', views.route_review, name='route_review'),
    path('<int:route_id>/add_event', views.route_add_event, name='add_event'),
    path('add_route', views.route_add, name='add_route'),
    path("event/<event_id>", views.event_handler, name='event_info'),
    path("event/<event_id>/add_me", views.add_me_to_event, name='add_me'),
    path("event/<event_id>/approved_user", views.event_approved_user),
    path('<str:route_type>', views.route_filter, name='route_type'),
    path('<str:route_type>/<str:country>', views.route_filter, name='route_country'),
    path('<str:route_type>/<str:country>/<str:location>', views.route_filter, name='route_location'),

]
