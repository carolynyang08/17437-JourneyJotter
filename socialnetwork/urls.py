from django.urls import path, include
from django.urls import path
from socialnetwork import views

urlpatterns = [
    path('', views.stream_action, name='home'),
    path('global', views.stream_action, name='global'),
    # path('get-global', views.get_list, name='get-global'),
    # path('home', views.home_action, name='home'),
        
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    
    # path('add_post', views.add_post, name='add_post'),
    # path('add-comment', views.add_comment, name='add-comment'),
    
    path('profile', views.profile_action, name='profile'),
    path('other', views.other_profile_action, name='other'),
    # path('other/<int:id>', views.other_profile_action, name='other'),
    path('photo/<int:id>', views.get_photo, name='photo'), 
    # path('follow/<int:id>', views.follow_action, name='follow'),
    # path('unfollow/<int:id>', views.unfollow_action, name='unfollow'), 
    path('search-user', views.search_friends_action, name="search-user"),

    # path('unfollow/<int:id>', views.unfollow_action, name='unfollow'),
    # path('activities', views.activities_action, name='activities'),

    # path('clear_gemini', views.clear_gemini_action, name='clear_gemini'),
    
    path('gem_activities', views.get_gem_activities, name='gem_activities'),
    path('gem_activities_stream/<int:trip_id>', views.gem_activities_stream, name='gem_activities_stream'),
    path('add_query', views.add_query, name='add_query'),
    path('clear_gemini/<int:trip_id>', views.clear_gemini, name='clear_gemini'),
    path('add_liked_gem_activity', views.add_liked_gem_activity, name='add_liked_gem_activity'),
    path('add_la_note', views.add_la_note, name='add_la_note'),
    path('del_la', views.del_la, name='del_la'),
    path('add_la_trip', views.add_la_trip, name='add_la_trip'),

    path('map', views.map_action, name='map'), 
    path('flights/<int:trip_id>', views.flight_action, name='flights'), 

    path('my_trips', views.my_trips_action, name='my_trips'),
    path('get-trips', views.get_trips),
    path('add-trip', views.add_trip, name='add-trip'),
    path('delete-trip/<int:item_id>', views.delete_trip, name='delete-trip'),
    path('leave-trip/<int:item_id>', views.leave_trip, name='leave-trip'),

    path('trip/<int:id>', views.trip_action, name='trip'),
    path('get-activities/<int:id>', views.get_activities, name='get-activities'),
    path('add-activity', views.add_activity, name='add-activity'),
    path('delete-activity/<int:item_id>', views.delete_activity, name='delete-activity'),
    path('add-friend/<str:email>/<int:tripID>', views.add_friend, name='add-friend'),

    path('like/<int:flight_results_id>/<int:flight_search_id>/<int:trip_id>', views.like_flight, name='like'),
    path('unlike/<int:flight_results_id>/<int:flight_search_id>/<int:trip_id>', views.unlike_flight, name='unlike'),

    path('like_from_trip/<int:flight_results_id>/<int:trip_id>', views.like_flight_from_trip, name='like_from_trip'),
    path('unlike_from_trip/<int:flight_results_id>/<int:trip_id>', views.unlike_flight_from_trip, name='unlike_from_trip'),

    path('add/<int:flight_results_id>/<int:trip_id>', views.add_flight_to_trip, name='add'),
    path('unadd/<int:flight_results_id>/<int:trip_id>', views.unadd_flight_from_trip, name='unadd'),
]

