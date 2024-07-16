from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Flight(models.Model):
    departure_airport = models.CharField(max_length=3)
    departure_time = models.CharField(max_length=200)
    arrival_airport = models.CharField(max_length=3)
    arrival_time = models.CharField(max_length=200)
    duration = models.CharField(max_length=20)
    airplane = models.CharField(max_length=200)
    airline = models.CharField(max_length=200)
    travel_class = models.CharField(max_length=200)
    flight_number = models.CharField(max_length=200)
    extensions = models.CharField(max_length=500)

class FlightResults(models.Model):
    connections = models.ManyToManyField(Flight)
    liked = models.BooleanField(default=False)
    added_to_map = models.BooleanField(default=False)

class FlightSearch(models.Model):
    departure_airport = models.CharField(max_length=3, blank=False)
    arrival_airport = models.CharField(max_length=3, blank=False)
    outbound_date = models.CharField(max_length=200)
    return_date = models.CharField(max_length=200)
    possible_flights = models.ManyToManyField(FlightResults)


# contains entire profile -> bio + picture
class Profile(models.Model):
    bio = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=True)
    picture_url = models.URLField(blank=True, max_length=1096)
    content_type = models.CharField(blank=True, max_length=50)
    following = models.ManyToManyField(User, related_name='followers')

    def __str__(self):
      return f'id={self.user.id}, text="{self.bio}", pic="{self.picture}'

class GeminiText(models.Model):
    query_text = models.CharField(max_length=1000)
    gemini_text = models.CharField(max_length=10000)
    query_time = models.DateTimeField()
    creator = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    
    def __str__(self):
        return f'id={self.creator.id}, query_text="{self.query_text}", query_time={str(self.query_time)}, creator={self.creator},gemini_text={self.gemini_text}'

class Destination(models.Model):
    arrival_time = models.DateTimeField()
    departure_time = models.DateTimeField()
    
    def __str__(self):
        return f'id={self.creator.id}, text="{self.text}", comment_time={str(self.comment_time)}, creator={self.creator}, post_id={self.post.id}'


class GemActivity(models.Model):
    # gem_query = models.ForeignKey(GeminiText, default=None, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    creator = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    creation_time = models.DateTimeField()
    note = models.CharField(max_length=200)
    add_to_trip = models.BooleanField(default=False)

    def __str__(self):
        return f'id={self.creator.id}, trip="{self.trip}", name={self.name}, address={self.address}, creator={self.creator}, creation_time={str(self.creation_time)}'


class Trip(models.Model):
    destination = models.CharField(max_length=200)
    destination_id = models.CharField(max_length=200)
    common_name = models.CharField(max_length=200)
    picture = models.CharField(max_length=200)
    creation_time = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    travelers = models.ManyToManyField(User, related_name='trips')

    flight_results = models.ManyToManyField(FlightResults)
    activities = models.ManyToManyField(GemActivity)
    
    def __str__(self):
        return f'id={self.creator.id}'

class Activity(models.Model):
    trip = models.ForeignKey(Trip, default=None, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    creator = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    creation_time = models.DateTimeField()
    place_id = models.CharField(max_length=200)
    # summary = models.CharField(max_length=200)
    # start_time = models.DateTimeField()
    # end_time = models.DateTimeField()
    
    def __str__(self):
        return f'id={self.creator.id}, trip="{self.trip}", name={self.name}, address={self.address}, creator={self.creator}, creation_time={str(self.creation_time)}'


class Stay(models.Model):
    trip = models.ForeignKey(Trip, default=None, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    checkin_time = models.DateTimeField()
    checkout_time = models.DateTimeField()
    price = models.CharField(max_length=200)
    reservation_file = models.FileField(blank=True)
    
    def __str__(self):
        return f'id={self.creator.id}, text="{self.text}", comment_time={str(self.comment_time)}, creator={self.creator}, post_id={self.post.id}'
