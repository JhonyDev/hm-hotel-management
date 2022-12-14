from django.contrib.auth.models import AbstractUser
from django.db import models

from src.accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=500)
    cost_per_night = models.PositiveIntegerField(default=0)
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.name)


class Room(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Booking(models.Model):
    OPTIONS = (
        ('Option-1', 'Option-1'),
        ('Option-2', 'Option-2'),
    )
    CATEGORIES = (
        ('Company', 'Company'),
        ('Walking', 'Walking'),
    )
    created_on = models.DateTimeField(max_length=500, auto_now_add=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_rooms = models.PositiveIntegerField(default=None, null=True, blank=True)
    customer_name = models.CharField(max_length=500, null=True, blank=True)
    company_name = models.CharField(max_length=500, null=True, blank=True, default=None)
    expected_number_of_people = models.PositiveIntegerField(default=0)
    total_cost_of_bookings = models.PositiveIntegerField(default=0)
    payment_type = models.CharField(default=None, max_length=500, null=True, blank=True)
    executive_per_night_cost = models.PositiveIntegerField(default=0)
    deluxe_per_night_cost = models.PositiveIntegerField(default=0)
    single = models.PositiveIntegerField(default=0)
    double = models.PositiveIntegerField(default=0)
    triple = models.PositiveIntegerField(default=0)
    quad = models.PositiveIntegerField(default=0)
    room_number = models.CharField(default=None, max_length=100, null=True, blank=True)
    note = models.TextField(default="", blank=True, null=True)
    customer_phone = models.CharField(max_length=500)
    customer_email = models.EmailField(max_length=500, null=True, blank=True, default=None)
    customer_cnic = models.CharField(max_length=500, null=True, blank=True, default=None)
    category = models.CharField(max_length=500, choices=CATEGORIES, default=None, null=True, blank=True)
    options = models.CharField(max_length=500, choices=OPTIONS, default=None, null=True, blank=True)
    rooms = models.ManyToManyField(Room)
    per_night_cost = models.PositiveIntegerField(default=0)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="manager+")
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="deleted_by_user+")
    is_active = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    booking_base_64 = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.customer_name)


class BookingPayment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    entry_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.PositiveIntegerField(default=None, null=True, blank=True)
    payment_date_time = models.PositiveBigIntegerField(null=True, blank=True, default=None)
    is_deleted = models.BooleanField(default=False)


class Service(models.Model):
    CATEGORIES = (
        ('Meal', 'Meal'),
        ('Meeting Hall', 'Meeting Hall'),
        ('Meal + Meeting Hall', 'Meal + Meeting Hall'),
    )
    service_type = models.CharField(max_length=500, choices=CATEGORIES, default=None, null=True, blank=True)
    company_name = models.CharField(max_length=500, default=None, null=True, blank=True)
    meal = models.CharField(max_length=500, default=None, null=True, blank=True)
    reservation_date = models.DateField()
    reservation_time = models.CharField(max_length=500, default=None, null=True, blank=True)
    number_of_persons = models.PositiveIntegerField(default=None, null=True, blank=True)
    rate_per_head = models.PositiveIntegerField(default=None, null=True, blank=True)
    note = models.CharField(max_length=500, default=None, null=True, blank=True)
    menu_option = models.CharField(max_length=500, default=None, null=True, blank=True)
    advance_payment = models.CharField(max_length=500, default=None, null=True, blank=True)
    conference_room_name = models.CharField(max_length=500, default=None, null=True, blank=True)
    conference_room_rate = models.CharField(max_length=500, default=None, null=True, blank=True)
    service_base_64 = models.TextField(default=None, null=True, blank=True)
