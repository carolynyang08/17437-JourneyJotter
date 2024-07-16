from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import RemoteUserBackend


from datetime import datetime
from django.utils import timezone
from django.utils.timezone import get_current_timezone

from socialnetwork.forms import LoginForm, RegisterForm, ProfileForm, FlightSearchForm 
from socialnetwork.models import Profile, GeminiText, Flight, FlightResults, FlightSearch, Trip, Activity, GemActivity

from django.core.exceptions import ObjectDoesNotExist
import json
import html
from serpapi import GoogleSearch
import google.generativeai as genai
import markdown

from pathlib import Path
from configparser import ConfigParser
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / "config.ini")
FLIGHTS_API_KEY = CONFIG.get("Flights", "secret")
GOOGLE_API_KEY = CONFIG.get("Google", "secret").replace("'", "")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


def login_action(request):
  context = {}
  if request.method == "GET":
    context['form'] = LoginForm()      
    return render(request, "socialnetwork/login.html", context)
  
  if ('username' not in request.POST or not request.POST['username']):
    context['error'] = 'Invalid Username/Password'
  
  if ('password' not in request.POST or not request.POST['password']):
    context['error'] = 'Invalid Username/Password'

  form = LoginForm(request.POST)
  context['form'] = form

  if not form.is_valid():
      context['error'] = 'Invalid Username/Password'
      return render(request, 'socialnetwork/login.html', context)

  new_user = authenticate(username=form.cleaned_data['username'],
                          password=form.cleaned_data['password'])

  login(request, new_user)

  return redirect(reverse('global'))

def register_action(request):
  context = {}

  if request.method == 'GET':
      context['form'] = RegisterForm()
      return render(request, 'socialnetwork/login.html', context)
  
  if ('first_name' not in request.POST or not request.POST['first_name']):
    context['register_error'] = 'Fill in fields'

  if ('last_name' not in request.POST or not request.POST['last_name']):
    context['register_error'] = 'Fill in fields'

  if ('username' not in request.POST or not request.POST['username']):
    context['register_error'] = 'Fill in fields'
  
  if ('password' not in request.POST or not request.POST['password']):
    context['register_error'] = 'Fill in fields'
  
  if ('email' not in request.POST or not request.POST['email']):
    context['register_error'] = 'Fill in fields'

  form = RegisterForm(request.POST)
  context['form'] = form

  if not form.is_valid():
    context['register_error'] = 'Fill in fields'
    return render(request, 'socialnetwork/login.html', context)

  new_user = User.objects.create_user(first_name=form.cleaned_data['first_name'],
                                      last_name=form.cleaned_data['last_name'],
                                      username=form.cleaned_data['username'], 
                                      password=form.cleaned_data['password'],
                                      email=form.cleaned_data['email'],
                                      )
  new_user.save()
  new_user = authenticate(username=form.cleaned_data['username'],
                          password=form.cleaned_data['password'])
  
  new_profile = Profile(user=new_user)
  new_profile.save()

  login(request, new_user)
  return redirect(reverse('global'))

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

 
@login_required

def stream_action(request):

  context = {}
  trips_data = []
  for trip in request.user.trips.all():
    trips_data.append(trip.id)
  context['trips'] = trips_data
  if hasattr(request.user, 'profile'):
    context['on_global_page'] = 'true'
    return render(request, "socialnetwork/global_stream.html", context)
  if request.user.social_auth.get(provider='google-oauth2'):
    user_picture_url = request.user.social_auth.get(provider='google-oauth2').extra_data['picture']
    new_user = User.objects.get(id=request.user.id)

  if not hasattr(new_user, 'profile'):
    profile = Profile(user=new_user, picture_url=user_picture_url)
    profile.save()
  else:
    profile =Profile.objects.get(id=request.user.id)
    profile.picture_url = user_picture_url
    profile.save()
  context['on_global_page'] = 'true'

  
    
  return render(request, "socialnetwork/global_stream.html", context)	

  
@login_required
def profile_action(request):
  context = {}
  current_user = request.user
  trips_data = []
  for trip in request.user.trips.all():
    trips_data.append(trip.id)
  context['trips'] = trips_data
  my_trips = Trip.objects.filter(creator=current_user.id)

  if request.method == "GET": 
    context['form'] = ProfileForm(initial={'bio': request.user.profile.bio})   
    return render(request, "socialnetwork/profile.html", context)

  form = ProfileForm(request.POST, request.FILES)
  if not form.is_valid():
    context = {'form': form}
    context['my_trips'] = my_trips
    return render(request, "socialnetwork/profile.html", context) 
  
  profile = get_object_or_404(Profile, id=request.user.id)
  profile.picture = form.cleaned_data['picture']
  profile.content_type = form.cleaned_data['picture'].content_type
#   profile.bio = form.cleaned_data['bio']
  profile.save()
  context = {'form': ProfileForm(initial={'bio': request.user.profile.bio})} 
  
  return render(request, "socialnetwork/profile.html", context)  

@login_required
def search_friends_action(request):
  context = {}
  if ('user_searched' not in request.POST or not request.POST['user_searched']):
    context['error'] = 'Error: Enter a search'
    if request.POST.get('other_profile') == "true":
      if request.POST.get('search_user_id') is not None:

        user = User.objects.filter(id=int(request.POST.get('search_user_id'))).first()
        context['searched_user'] = user
        context['other_profile'] = 'true'
        context['search_user_id'] = str(user.id)
       
      return render(request, "socialnetwork/other_profile.html", context)

    else:
      context['form'] = ProfileForm(initial={'bio': request.user.profile.bio})
      return render(request, "socialnetwork/profile.html", context) 

  searched_user = request.POST['user_searched']
  users_by_username = User.objects.filter(email=searched_user)
  users_by_email = User.objects.filter(username=searched_user)
  if users_by_username or users_by_email:
    found_user_by_username = users_by_username.first()
    found_user_by_email = users_by_email.first()
    if found_user_by_username:
       found_user = found_user_by_username
    elif found_user_by_email:
       found_user = found_user_by_email

    if (found_user == request.user):
      context = {'form': ProfileForm(initial={'bio': request.user.profile.bio})}  
      return render(request, "socialnetwork/profile.html", context)
    else:
      context = {'searched_user': found_user, 'other_profile': 'true', 'search_user_id': str(found_user.id)}
      return render(request, "socialnetwork/other_profile.html", context)
   
  else:
    context['error'] = "Error: Enter a valid user"
    if request.POST.get('other_profile') == "true":
      if request.POST.get('search_user_id') is not None:

        user = User.objects.filter(id=int(request.POST.get('search_user_id'))).first()
        context['searched_user'] = user
        context['other_profile'] = 'true'
        context['search_user_id'] = str(user.id)
      return render(request, "socialnetwork/other_profile.html", context)
    else:
      context['form'] = ProfileForm(initial={'bio': request.user.profile.bio})
      return render(request, "socialnetwork/profile.html", context) 



@login_required    
def other_profile_action(request):
  
  return render(request, "socialnetwork/other_profile.html")

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))
 
@login_required
def get_photo(request, id):
    item = get_object_or_404(Profile, id=id)
    
    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.picture:
        raise Http404

    return HttpResponse(item.picture, content_type=item.content_type)

def google_oauth(request):
  context = {}
  return render(request, "socialnetwork/google_oauth.html", context)

def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)
  
######################################################

# Gemini

######################################################

@login_required
def gem_activities_stream(request, trip_id):
  if not request.user.is_authenticated:
    return _my_json_error_response("You must be logged in to do this operation", status=401)
  requestor = get_object_or_404(User, id=request.user.id)
  trip = get_object_or_404(Trip, id=trip_id)
  if ((trip.creator != requestor) and (requestor not in trip.travelers.all())):
    return _my_json_error_response("You cannot search activities for a trip you're not a part of.", status=403)
    

  # ordering in reverse chronological order
  gemini_queries = GeminiText.objects.all().order_by("-query_time")
  context = {'gemini_queries': gemini_queries, 'trip_id': trip_id}
  
  if request.method == "GET":    
    return render(request, "socialnetwork/gemini_activities.html", context)
  
  if ('text' not in request.POST or not request.POST['text']):
    context['error'] = 'Error: your post requires a body of text.'
    return render(request, "socialnetwork/gemini_activities.html", context)
  
  return redirect('gem_activities_stream')
  
def get_gem_activities(request):
        if not request.user.is_authenticated:
            return _my_json_error_response("You must be logged in to do this operation", status=401)

        response_data = {'gemini_queries': [], 'liked_activities': []}
        for gem_query in GeminiText.objects.all():
            my_item = {
                    'id': gem_query.id,
                    'query_text': gem_query.query_text,
                    'gemini_text': gem_query.gemini_text,
                    'first_name': gem_query.creator.first_name,
                    'last_name': gem_query.creator.last_name,
                    'query_time': gem_query.query_time.isoformat(),
            }
            response_data['gemini_queries'].append(my_item)
        for likedActivity in GemActivity.objects.all():
            my_item = {
                    'name': likedActivity.name,
                    'creation_time': likedActivity.creation_time.isoformat(),
                    'note': likedActivity.note,
                    'add_to_trip': likedActivity.add_to_trip,
            }
            response_data['liked_activities'].append(my_item)

        response_json = json.dumps(response_data)

        return HttpResponse(response_json, content_type='application/json')
  
def add_query(request):
        if not request.user.is_authenticated:
                return _my_json_error_response("You must be logged in to do this operation", status=401)

        if request.method != 'POST':
                return _my_json_error_response("You must use a POST request for this operation", status=405)

        # if not (('gem_query_item' in request.POST or not request.POST['gem_query_item']) or ('trip_id' in request.POST or not request.POST['trip_id'])):
        if not (('gem_query_item' in request.POST or not request.POST['gem_query_item'])):
                return _my_json_error_response("You must enter text to query gemini.", status=400)
    
        query = request.POST['gem_query_item']
        trip_id = request.POST['trip_id']
        trip_id_num = int(trip_id.replace("/", ""))
        trip = get_object_or_404(Trip, id=trip_id_num)
        if (">" in query or "<" in query or '"' in query or "&" in query or "'" in query or '`' in query):
            return _my_json_error_response("No evil queries >:-(", status=400)
    
    # getting gemini response
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(query)
  
        DateTime_in_ISOFormat = datetime.now(tz=get_current_timezone())
        DateTime_in_ISOFormat = DateTime_in_ISOFormat.isoformat("T", "microseconds")
  
        new_item = GeminiText(
        query_text=query, 
        gemini_text=markdown.markdown(response.text),
        query_time=DateTime_in_ISOFormat, 
        creator=request.user)
        new_item.save()

        return get_gem_activities(request)

def clear_gemini(request, trip_id):
    # Delete all objects from the GeminiText model
    GeminiText.objects.all().delete()
    
    # Redirect to the activities page or any other page you want
    gemini_queries = GeminiText.objects.all().order_by("-query_time")
    context = {'gemini_queries': gemini_queries}
    return redirect('gem_activities_stream', trip_id=trip_id)

def add_liked_gem_activity(request):
        if not request.user.is_authenticated:
                return _my_json_error_response("You must be logged in to do this operation", status=401)

        if request.method != 'POST':
                        return _my_json_error_response("You must use a POST request for this operation", status=405)

        if not 'liked_gem_activity' in request.POST or not request.POST['liked_gem_activity']:
                        return _my_json_error_response("Activity name not correctly captured.", status=400)

        liked_activity = request.POST['liked_gem_activity']
        trip_id = request.POST['trip_id']
        trip_id_num = int(trip_id.replace("/", ""))
        trip = get_object_or_404(Trip, id=trip_id_num)

        DateTime_in_ISOFormat = datetime.now(tz=get_current_timezone())
        DateTime_in_ISOFormat = DateTime_in_ISOFormat.isoformat("T", "microseconds")

        new_item = GemActivity(
        name=liked_activity,
        creator=request.user,
        creation_time=DateTime_in_ISOFormat, 
        note='', # default value because activity has only been liked so far
        )
        new_item.save()

        return get_gem_activities(request)

def add_la_note(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
            return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not (('la_note' in request.POST or not request.POST['la_note']) or ('act_name' in request.POST or not request.POST['act_name'])):
            return _my_json_error_response("Liked activity note not correctly captured or activity name not captured.", status=400)
 
    la_note = request.POST['la_note']
    if (">" in la_note or "<" in la_note or '"' in la_note or "&" in la_note or "'" in la_note or '`' in la_note):
            return _my_json_error_response("No evil notes >:-(", status=400)
 
    act_name = request.POST['act_name']
 
    # need to update model
    la = GemActivity.objects.get(name=act_name)
    la.note = la_note
    # updating creation time so la moves to top of column
    DateTime_in_ISOFormat = datetime.now(tz=get_current_timezone())
    DateTime_in_ISOFormat = DateTime_in_ISOFormat.isoformat("T", "microseconds")
    la.creation_time = DateTime_in_ISOFormat
    la.save()

    return get_gem_activities(request)

def del_la(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
            return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not ('act_name' in request.POST or not request.POST['act_name']):
            return _my_json_error_response("Unable to delete note.", status=400)
    
    act_name = request.POST['act_name']
 
    # need to update model
    la = GemActivity.objects.get(name=act_name)
    la.delete()

    return get_gem_activities(request)

def add_la_trip(request):
        if not request.user.is_authenticated:
                return _my_json_error_response("You must be logged in to do this operation", status=401)

        if request.method != 'POST':
                        return _my_json_error_response("You must use a POST request for this operation", status=405)

        if not ('act_name' in request.POST or not request.POST['act_name']):
                        return _my_json_error_response("Unable to add to trip.", status=400)
                
        act_name = request.POST['act_name']
        trip_id = request.POST['trip_id']
        trip_id_num = int(trip_id.replace("/", ""))

    # need to update model
        la = GemActivity.objects.get(name=act_name)
        trip_to_add = Trip.objects.get(id=trip_id_num)
        # la_trip = la.trip_id
        # trip_to_add.activities.add(la)
        # trip_to_add.save()
    
        if (la.add_to_trip):
                la.add_to_trip = False	
                trip_to_add.activities.remove(la)
                trip_to_add.save()
        else:
                la.add_to_trip = True
                trip_to_add.activities.add(la)
                trip_to_add.save()
        la.save()

        return get_gem_activities(request)
  

def check_flights(trip):
    for flight_search in trip.flight_results.all():
        for flight in flight_search.connections.all():
            flight_found = False
            departure_airport = flight.departure_airport
            departure_date = flight.departure_time.split(" ")[0]
            arrival_airport = flight.arrival_airport
            arrival_date = flight.arrival_time.split(" ")[0]
            flight_number = flight.flight_number
            params = {
            "engine": "google_flights",
            "departure_id": departure_airport,
            "arrival_id": arrival_airport,
            "outbound_date": departure_date,
            "return_date": arrival_date,
            "api_key": FLIGHTS_API_KEY.replace("'", "")
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            try:
                best_flights = results["best_flights"]
                for bf in best_flights:
                    details = bf["flights"]
                    for detail in details:
                        poss_flight_number = detail["flight_number"]
                        if poss_flight_number == flight_number:
                            flight_found = True
                            flight.departure_time = detail["departure_airport"]["time"]
                            flight.arrival_time = detail["arrival_airport"]["time"]
                            flight.duration = detail["duration"]
                            flight.airplane = detail["airplane"]
                            flight.travel_class = detail["travel_class"]
                            flight.extensions = detail["extensions"]
                            flight.save()
                if not flight_found:
                    try:
                        other_flights = results["other_flights"]
                        for bf in other_flights:
                            details = bf["flights"]
                            for detail in details:
                                poss_flight_number = detail["flight_number"]
                                if poss_flight_number == flight_number:
                                    flight_found = True
                                    flight.departure_time = detail["departure_airport"]["time"]
                                    flight.arrival_time = detail["arrival_airport"]["time"]
                                    flight.duration = detail["duration"]
                                    flight.airplane = detail["airplane"]
                                    flight.travel_class = detail["travel_class"]
                                    flight.extensions = detail["extensions"]
                                    flight.save()
                        if not flight_found:
                            trip.flight_results.remove(flight_search)
                            trip.save()
                    except:
                        trip.flight_results.remove(flight_search)
                        trip.save()
            except:
                trip.flight_results.remove(flight_search)
                trip.save()
  

######################################################

# Flights

######################################################

@login_required
def like_flight(request, flight_results_id, flight_search_id, trip_id):
    context = {}
    context['form'] = FlightSearchForm()
    context["trip_id"] = trip_id
    flight_result = get_object_or_404(FlightResults, id=flight_results_id)
    flight_result.liked = True
    flight_result.save()
    trip = get_object_or_404(Trip, id=trip_id)
    check_flights(trip)
    trip.flight_results.add(flight_result)
    trip.save()
    context["trip"] = trip
    context["new_flightsearch"] = get_object_or_404(FlightSearch, id=flight_search_id)
    return render(request, 'socialnetwork/flights.html', context)

@login_required
def unlike_flight(request, flight_results_id, flight_search_id, trip_id):
    context = {}
    context['form'] = FlightSearchForm()
    context["trip_id"] = trip_id
    flight_result = get_object_or_404(FlightResults, id=flight_results_id)
    flight_result.liked = False
    flight_result.save()
    trip = get_object_or_404(Trip, id=trip_id)
    check_flights(trip)
    trip.flight_results.remove(flight_result)
    trip.save()
    context["trip"] = trip
    context["new_flightsearch"] = get_object_or_404(FlightSearch, id=flight_search_id)
    return render(request, 'socialnetwork/flights.html', context)

@login_required
def like_flight_from_trip(request, flight_results_id, trip_id):
    context = {}
    context["trip_id"] = trip_id
    flight_result = get_object_or_404(FlightResults, id=flight_results_id)
    flight_result.liked = True
    flight_result.save()
    trip = get_object_or_404(Trip, id=trip_id)
    check_flights(trip)
    trip.flight_results.add(flight_result)
    trip.save()
    context["trip"] = trip
    return render(request, "socialnetwork/trip.html", context)

@login_required
def unlike_flight_from_trip(request, flight_results_id, trip_id):
    context = {}
    context["trip_id"] = trip_id
    flight_result = get_object_or_404(FlightResults, id=flight_results_id)
    flight_result.liked = False
    flight_result.save()
    trip = get_object_or_404(Trip, id=trip_id)
    check_flights(trip)
    trip.flight_results.remove(flight_result)
    trip.save()
    context["trip"] = trip
    return render(request, "socialnetwork/trip.html", context)

@login_required
def add_flight_to_trip(request, flight_results_id, trip_id):
    context = {}
    context["trip_id"] = trip_id
    flight_result = get_object_or_404(FlightResults, id=flight_results_id)
    flight_result.added_to_map = True
    flight_result.save()
    trip = get_object_or_404(Trip, id=trip_id)
    check_flights(trip)
    trip.flight_results.add(flight_result)
    trip.save()
    context["trip"] = trip
    return render(request, "socialnetwork/trip.html", context)

@login_required
def unadd_flight_from_trip(request, flight_results_id, trip_id):
    context = {}
    context["trip_id"] = trip_id
    flight_result = get_object_or_404(FlightResults, id=flight_results_id)
    flight_result.added_to_map = False
    flight_result.save()
    trip = get_object_or_404(Trip, id=trip_id)
    check_flights(trip)
    context["trip"] = trip
    return render(request, "socialnetwork/trip.html", context)


@login_required
def flight_action(request, trip_id):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    requestor = get_object_or_404(User, id=request.user.id)
    trip = get_object_or_404(Trip, id=trip_id)
    if ((trip.creator != requestor) and (requestor not in trip.travelers.all())):
        return _my_json_error_response("You cannot add flights to a trip you're not a part of.", status=403)
     
    context = {}
    context['form'] = FlightSearchForm()
    trip = get_object_or_404(Trip, id=trip_id)
    check_flights(trip)
    context["trip"] = trip
    context["trip_id"] = trip_id
    if request.method == "GET":
        return render(request, "socialnetwork/flights.html", context)

    if "departure_airport" not in request.POST or "arrival_airport" not in request.POST or "outbound_date" not in request.POST or "return_date" not in request.POST:
        context["message"] = "A required field is missing from request.POST"
        return render(request, "socialnetwork/flights.html", context)
    
    form = FlightSearchForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'socialnetwork/flights.html', context)

    print(request.POST)
    departure_airport = request.POST["departure_airport"].split(":")[0]
    arrival_airport = request.POST["arrival_airport"].split(":")[0]
    outbound_date = request.POST["outbound_date"]
    return_date = request.POST["return_date"]
    hl = request.POST["hl"]
    currency = request.POST["currency"]
    travel_class = request.POST["travel_class"]
    adults = request.POST["adults"]
    children = request.POST["children"]
    infants_in_seat = request.POST["infants_in_seat"]
    infants_on_lap = request.POST["infants_on_lap"]
    stop = request.POST["stop"]
    bags = request.POST["bags"]
    minimum_layover = request.POST["minimum_layover"]
    maximum_layover = request.POST["maximum_layover"]
    max_duration = request.POST["max_duration"]

    if (">" in departure_airport or "<" in departure_airport or '"' in departure_airport or "&" in departure_airport or "'" in departure_airport or '`' in departure_airport):
        return _my_json_error_response("No evil queries >:-(", status=400)
    if (">" in arrival_airport or "<" in arrival_airport or '"' in arrival_airport or "&" in arrival_airport or "'" in arrival_airport or '`' in arrival_airport):
        return _my_json_error_response("No evil queries >:-(", status=400)
    
    new_flightsearch = FlightSearch(departure_airport=departure_airport,
                                 arrival_airport=arrival_airport,
                                 outbound_date=outbound_date,
                                 return_date=return_date)

    new_flightsearch.save()
    params = {
    "engine": "google_flights",
    "departure_id": departure_airport,
    "arrival_id": arrival_airport,
    "outbound_date": outbound_date,
    "return_date": return_date,
    "travel_class": travel_class,
    "hl": hl,
    "currency": currency,
    "adults": adults,
    "children": children,
    "infants_in_seat": infants_in_seat,
    "infants_on_lap": infants_on_lap,
    "stops": stop,
    "bags": bags,
    "max_duration": max_duration,
    "api_key": FLIGHTS_API_KEY.replace("'", "")
     }
    search = GoogleSearch(params)
    results = search.get_dict()
    try:
        best_flights = results["best_flights"]
    except:
        try:
            x = results["error"]
            error_message = f"no flights found: {x}"
        except:
            error_message = f"no flights found"
        message = error_message
        context["message"] = message
        return render(request, "socialnetwork/flights.html", context)
    for flight in best_flights:
        details = flight["flights"]
        new_flightresults = FlightResults()
        new_flightresults.save()
        for detail in details: #detail is a dictionary
            departure_airport = detail["departure_airport"]["id"]
            departure_time = detail["departure_airport"]["time"]
            arrival_airport = detail["arrival_airport"]["id"]
            arrival_time = detail["arrival_airport"]["time"]
            duration = detail["duration"]
            airplane = detail["airplane"]
            airline = detail["airline"]
            travel_class = detail["travel_class"]
            flight_number = detail["flight_number"]
            extensions = detail["extensions"]
            new_flight = Flight(departure_airport=departure_airport,
                       departure_time=departure_time,
                       arrival_airport=arrival_airport,
                       arrival_time=arrival_time,
                       duration=duration,
                       airplane=airplane,
                       airline=airline,
                       travel_class=travel_class,
                       flight_number=flight_number,
                       extensions=extensions)
            new_flight.save()
            new_flightresults.connections.add(new_flight)
            new_flightresults.save()
        new_flightsearch.possible_flights.add(new_flightresults)
        new_flightsearch.save()
    context["new_flightsearch"] = new_flightsearch
    return render(request, "socialnetwork/flights.html", context)

######################################################

# Map

######################################################

def map_action(request):
  context = {}
  return render(request, "socialnetwork/maps.html", context)

######################################################

# Trips

######################################################


@login_required
def my_trips_action(request):
    context = {}
    trips_data = []
    for trip in request.user.trips.all():
        trips_data.append(trip.id)
    context['trips'] = trips_data
    return render(request, 'socialnetwork/my_trips.html', context)

def get_trips(request):

    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    if (request.GET.get('other_user_id')):
        trip_user = User.objects.filter(id=request.GET.get('other_user_id')).first()
    
    else:
        trip_user = request.user

    trips_data = []
    trips = Trip.objects.all().order_by('start_date')

    #On global page so we grab last 20 trips 
    if (request.GET.get('on_global_page')) == 'true':
        triplist = Trip.objects.order_by('-start_date')[:10]
    else:
        # Filter trips by creator
        triplist = []
        for trip in trips:
        # if ((trip.creator == request.user) or (request.user in trip.travelers.all())):
            if ((trip.creator == trip_user) or (trip_user in trip.travelers.all())):
                triplist.append(trip)

    # Generate data
    for model_item in triplist:
        my_item = {
            'id': model_item.id,
            'destination': model_item.destination,
            'destination_id': model_item.destination_id,
            'picture': model_item.picture,
            'creation_time': model_item.creation_time.isoformat(),
            'creator_id': model_item.creator.id,
            'creator': model_item.creator.username,
            'start_date': model_item.start_date.isoformat(),
            'end_date': model_item.end_date.isoformat(),
            'common_name': model_item.common_name,
        }
        trips_data.append(my_item)

    response_data = {'trips': trips_data}

    response_json = json.dumps(response_data)

    #return JSON for my trips ordered by start date
    return HttpResponse(response_json, content_type='application/json')

def add_trip(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
        
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
            
    if not 'destination' in request.POST or not request.POST['destination']:
        return _my_json_error_response("You must enter a destination.", status=400)

    if not 'common_name' in request.POST or not request.POST['common_name']:
        return _my_json_error_response("Invalid common_name.", status=400)

    if not 'destination_id' in request.POST or not request.POST['destination_id']:
        return _my_json_error_response("Invalid destination.", status=400)

    if not 'start_date' in request.POST or not request.POST['start_date']:
        return _my_json_error_response("You must enter a start date.", status=400)

    if not 'end_date' in request.POST or not request.POST['end_date']:
        return _my_json_error_response("You must enter an end date.", status=400)

    new_trip = Trip(destination=request.POST['destination'], common_name=request.POST['common_name'], destination_id=request.POST['destination_id'], picture=request.POST['picture'], creator=request.user, creation_time=timezone.now(), start_date=request.POST['start_date'], end_date=request.POST['end_date'])
    new_trip.save()

    trips_data = []
    my_trip = {
        'id': new_trip.id,
        'destination': new_trip.destination,
        'destination_id': new_trip.destination_id,
        'picture': new_trip.picture,
        'common_name': new_trip.common_name,
        'creation_time': new_trip.creation_time.isoformat(),
        'creator_id': new_trip.creator.id,
        'creator': new_trip.creator.username,
        'start_date': new_trip.start_date,
        'end_date': new_trip.end_date,
        }
    trips_data.append(my_trip)

    response_data = {'trips': trips_data}

    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

@login_required
def delete_trip(request, item_id):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    try:
        trip = Trip.objects.get(id=item_id)
    except ObjectDoesNotExist:
        return _my_json_error_response(f"Item with id={item_id} does not exist.", status=404)

    if request.user.email != trip.creator.email:
        return _my_json_error_response("You cannot delete other user's entries", status=403)

    # Delete all activities in trip

    activities = Activity.objects.all()

    for activity in activities:
        if (activity.trip == trip):
            delete_activity(request, activity.id)

    trip.delete()

    return get_trips(request)

@login_required
def leave_trip(request, item_id):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    requestor = get_object_or_404(User, id=request.user.id)
    trip = get_object_or_404(Trip, id=item_id)
    if ((trip.creator != requestor) and (requestor not in trip.travelers.all())):
        return _my_json_error_response("You cannot leave a trip you're not a part of.", status=403)
        
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    try:
        trip = Trip.objects.get(id=item_id)
    except ObjectDoesNotExist:
        return _my_json_error_response(f"Item with id={item_id} does not exist.", status=404)

    if (request.user == trip.creator):
        travelers = trip.travelers.all()
        if not travelers:
            # Case 1: user is the creator, and there are no more travelers
            delete_trip(request, item_id)
        else:
            # Case 2: user is the creator, and there are other travelers
            new_owner = travelers[0] # make next user the owner
            user = get_object_or_404(User, id=new_owner.id)
            trip.creator = new_owner
            user.trips.remove(trip)
            trip.save()

    else:
        # case 3: the user is not part of the trip
        if (not (request.user in trip.travelers.all())):
            return _my_json_error_response("You cannot leave a trip you are not a part of.", status=403)
        else:
            # case 4: the user is a traveler, but not the owner:
            user = get_object_or_404(User, id=request.user.id)
            user.trips.remove(trip)
            trip.save()

    return get_trips(request)

@login_required
def add_friend(request, email, tripID):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    requestor = get_object_or_404(User, id=request.user.id)
    trip = get_object_or_404(Trip, id=tripID)
    if ((trip.creator != requestor) and (requestor not in trip.travelers.all())):
        return _my_json_error_response("You cannot add friends to a trip you're not a part of.", status=403)
    
    trip = get_object_or_404(Trip, id=tripID)
    user = get_object_or_404(User, email=email)
    trip.travelers.add(user)
    trip.save()
    return get_activities(request, tripID)


######################################################

# Activities

######################################################

def trip_action(request, id):
    trip = get_object_or_404(Trip, id=id)
    check_flights(trip)
    return render(request, "socialnetwork/trip.html", {'trip_id':id, 'trip_destination':trip.destination, 'place_id':trip.destination_id, 'trip':trip})

def get_activities(request, id):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
        
    activities_data = []
    activities = Activity.objects.all().order_by('creation_time')
    
    # Filter activities by trip
    activitylist = []
    for activity in activities:
        if (activity.trip.id == id):
            activitylist.append(activity)

    # Generate data
    for model_item in activitylist:
        my_item = {
            'id': model_item.id,
            'trip_id': model_item.trip.id,
            'name': model_item.name,
            'creation_time': model_item.creation_time.isoformat(),
            'creator_id': model_item.creator.id,
            'creator': model_item.creator.username,
            'place_id': model_item.place_id,
        }
        activities_data.append(my_item)

    response_data = {'activities': activities_data}

    response_json = json.dumps(response_data)
    
    return HttpResponse(response_json, content_type='application/json')

@login_required
def add_activity(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
        
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
            
    if not 'trip_id' in request.POST or not request.POST['trip_id']:
        return _my_json_error_response("Bad trip id.", status=400)
    
    if not 'name' in request.POST or not request.POST['name']:
        return _my_json_error_response("You must enter a destination.", status=400)

    if not 'address' in request.POST or not request.POST['address']:
        return _my_json_error_response("You must enter a start date.", status=400)

    if not 'place_id' in request.POST or not request.POST['place_id']:
        return _my_json_error_response("Invalid Place ID", status=400)

    trip = get_object_or_404(Trip, id=request.POST['trip_id'])
    requestor = get_object_or_404(User, id=request.user.id)
    if ((trip.creator != requestor) and (requestor not in trip.travelers.all())):
        return _my_json_error_response("You cannot add activities to a trip you're not a part of.", status=403)
    
    new_activity = Activity(trip=trip, name=request.POST['name'], creator=request.user, creation_time=timezone.now(), place_id=request.POST['place_id'])
    new_activity.save()

    activities_data = []
    my_activity = {
        'id': new_activity.id,
            'trip_id': new_activity.trip.id,
            'name': new_activity.name,
            'creation_time': new_activity.creation_time.isoformat(),
            'creator_id': new_activity.creator.id,
            'creator': new_activity.creator.username,
            'place_id': new_activity.place_id,
        }
    activities_data.append(my_activity)

    response_data = {'activities': activities_data}

    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')


def delete_activity(request, item_id):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    try:
        activity = Activity.objects.get(id=item_id)
    except ObjectDoesNotExist:
        return _my_json_error_response(f"Item with id={item_id} does not exist.", status=404)

    if (request.user.email != activity.creator.email) and (not (request.user in activity.trip.travelers.all())):
        return _my_json_error_response("You cannot delete activities if you're not part of this trip.", status=403)

    activity.delete()

    return get_activities(request, activity.trip_id)

