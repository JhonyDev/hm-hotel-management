import datetime
from copy import copy
from datetime import date

from dateutil import parser
from django.shortcuts import get_object_or_404, render
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.settings import BASE_URL
from . import serializers, utils
from .models import Room, Category, Booking, BookingPayment
from ..accounts.authentication import JWTAuthentication
from ..accounts.models import User


class UsersListView(generics.ListCreateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(type="Manager")

    def perform_create(self, serializer):
        user = serializer.save()
        user.type = "Manager"
        user.save()


class UserDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        if not self.request.user.is_superuser:
            raise utils.get_api_exception("You are not allowed to update users details", status.HTTP_403_FORBIDDEN)
        pk = self.kwargs["pk"]
        return get_object_or_404(User, pk=pk)


class RoomRUV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Room, pk=pk)


class BookingPaymentListView(generics.ListCreateAPIView):
    serializer_class = serializers.BookingPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_queryset(self):
        pk = self.kwargs["pk"]
        booking = get_object_or_404(Booking, pk=pk)
        return BookingPayment.objects.filter(booking=booking)

    def perform_create(self, serializer):
        serializer.save(entry_by=self.request.user)


class BookingPaymentUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.BookingPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        booking = get_object_or_404(BookingPayment, pk=pk)
        return booking


class RoomsListView(generics.ListCreateAPIView):
    serializer_class = serializers.RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Room.objects.all()


class CategoryRUV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Category, pk=pk)


class CategoryListView(generics.ListCreateAPIView):
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Category.objects.all()


class CategoryCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.CategoryPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        categories = Category.objects.all()
        for category in categories:
            rooms = Room.objects.filter(category=category).count()
            category.number_of_rooms = rooms
        return categories

    def perform_create(self, serializer):
        category = serializer.save()
        for x in range(category.number_of_rooms):
            Room.objects.create(category=category)


class CategoryNumRUV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CategoryNumSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        category = get_object_or_404(Category, pk=pk)
        rooms = Room.objects.filter(category=category).count()
        category.number_of_rooms = rooms
        return category


class BookingRUV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Booking, pk=pk, manager=self.request.user)


class BookingListView(generics.ListCreateAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Booking.objects.filter(manager=self.request.user)

    def perform_create(self, serializer):
        booking = serializer.save(manager=self.request.user)
        bookings = Booking.objects.filter(check_in_date__gte=booking.check_in_date,
                                          check_out_date__lt=booking.check_in_date)
        if bookings.exists():
            booking.delete()
            raise ValidationError('Booking cannot be created, check in date conflicts with another booking')

        bookings = Booking.objects.filter(check_in_date__gt=booking.check_out_date,
                                          check_out_date__lte=booking.check_out_date)
        if bookings.exists():
            booking.delete()
            raise ValidationError('Booking cannot be created, check out date conflicts with another booking')


class BookingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        check_in_date = request.data['check_in_date']
        check_in_date = parser.parse(check_in_date, dayfirst=True)
        check_out_date = request.data['check_out_date']
        check_out_date = parser.parse(check_out_date, dayfirst=True)
        customer_name = request.data['customer_name']
        customer_phone = request.data['customer_phone']
        customer_email = request.data['customer_email']
        customer_cnic = request.data['customer_cnic']
        category = request.data['category']
        options = request.data['options']
        categories = request.data['categories']
        total_rooms = request.data['total_rooms']
        company_name = request.data['company_name']
        expected_number_of_people = request.data['expected_number_of_people']
        total_cost_of_bookings = request.data['total_cost_of_bookings']

        total_rooms = int(total_rooms)
        booking = Booking.objects.create(check_out_date=check_out_date,
                                         check_in_date=check_in_date,
                                         company_name=company_name,
                                         category=category,
                                         expected_number_of_people=expected_number_of_people,
                                         customer_name=customer_name,
                                         customer_phone=customer_phone,
                                         options=options,
                                         total_rooms=total_rooms,
                                         customer_email=customer_email,
                                         total_cost_of_bookings=total_cost_of_bookings,
                                         customer_cnic=customer_cnic)

        rooms_ = []
        warnings = []
        for category in categories:
            name = category['name']
            number_of_rooms = category['number_of_rooms']
            room_category = get_object_or_404(Category, name=name)
            if utils.get_availability(check_in_date, check_out_date)[name]["count"] >= number_of_rooms:
                rooms = Room.objects.filter(category=room_category)[:number_of_rooms]
                for room in rooms:
                    rooms_.append(room)
            else:
                warnings.append(f"{name} exceeds availability, cannot create booking")
        booking.rooms.set(rooms_)
        pdf = utils.generate_pdf_get_path(f"{BASE_URL}api/invoice/booking/{booking.pk}/")
        booking.booking_base_64 = utils.encode_base_64(pdf)
        booking.save()

        rooms = []
        for room in booking.rooms.all():
            rooms.append(room.pk)

        context = {
            'created_on': booking.created_on,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'total_rooms': booking.total_rooms,
            'customer_name': booking.customer_name,
            'customer_phone': booking.customer_phone,
            'customer_email': booking.customer_email,
            'customer_cnic': booking.customer_cnic,
            'category': booking.category,
            'options': booking.options,
            'rooms': rooms,
            'manager': booking.manager,
            'is_active': booking.is_active,
            'booking_base_64': booking.booking_base_64
        }

        return Response(data=context,
                        status=status.HTTP_200_OK)


class UpdateBookingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, pk, format=None):
        booking = get_object_or_404(Booking, pk=pk)

        check_in_date = request.data['check_in_date']
        booking.check_in_date = parser.parse(check_in_date, dayfirst=True)
        check_out_date = request.data['check_out_date']
        booking.check_out_date = parser.parse(check_out_date, dayfirst=True)
        booking.customer_name = request.data['customer_name']
        booking.customer_phone = request.data['customer_phone']
        booking.customer_email = request.data['customer_email']
        booking.customer_cnic = request.data['customer_cnic']
        booking.is_active = request.data['is_active']

        booking.save()
        pdf = utils.generate_pdf_get_path(f"{BASE_URL}api/invoice/booking/{booking.pk}/")
        booking.booking_base_64 = utils.encode_base_64(pdf)
        booking.save()

        categories = Category.objects.all()
        dict_ = {}
        for category in categories:
            dict_[category.name] = booking.rooms.filter(category=category).count()
        booking_dict = {
            'pk': booking.pk,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'customer_name': booking.customer_name,
            'customer_phone': booking.customer_phone,
            'customer_email': booking.customer_email,
            'customer_cnic': booking.customer_cnic,
            'total_rooms': booking.total_rooms,
            'options': booking.options,
            'categories': booking.category,
            'is_active': booking.is_active,
            'bookings': dict_,
            'booking_base_64': booking.booking_base_64,
        }

        return Response(data=booking_dict,
                        status=status.HTTP_200_OK)


class BookingGetAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, date_, format=None):
        date_ = parser.parse(date_, dayfirst=True)
        bookings = Booking.objects.filter(check_in_date__lte=date_, check_out_date__gte=date_)
        booking_array = []

        for booking in bookings:
            categories = Category.objects.all()
            dict_ = {}
            for category in categories:
                dict_[category.name] = booking.rooms.filter(category=category).count()
            booking_dict = {
                'pk': booking.pk,
                'check_in_date': booking.check_in_date,
                'check_out_date': booking.check_out_date,
                'customer_name': booking.customer_name,
                'customer_phone': booking.customer_phone,
                'customer_email': booking.customer_email,
                'customer_cnic': booking.customer_cnic,
                'total_rooms': booking.total_rooms,
                'company_name': booking.total_rooms,
                'booking_base_64': booking.booking_base_64,
                'options': booking.options,
                'category': booking.category,
                'is_active': booking.is_active,
                'expected_number_of_people': booking.expected_number_of_people,
                'total_cost_of_bookings': booking.total_cost_of_bookings,
            }
            booking_array.append(booking_dict)
        return Response(data=booking_array,
                        status=status.HTTP_200_OK)


class BookingRUVGeneral(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Booking, pk=pk)


class BookingListViewGeneral(generics.ListCreateAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Booking.objects.all()


class AvailabilityToday(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = date.today()
        end_date = today + datetime.timedelta(days=1)
        rooms = utils.get_availability(today, end_date)
        return Response(data=rooms,
                        status=status.HTTP_200_OK)


class AvailabilityTargetDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, date_, end_date_, *args, **kwargs):
        target_date = parser.parse(date_, dayfirst=True)
        target_end_date = parser.parse(end_date_, dayfirst=True)
        rooms = utils.get_availability(target_date, target_end_date)
        return Response(data=rooms,
                        status=status.HTTP_200_OK)


class BookingsMonth(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, month, year, *args, **kwargs):
        target_start_date, target_end_date = utils.get_target_dates(month, year)
        bookings = Booking.objects.filter(created_on__lte=target_end_date, created_on__gte=target_start_date,
                                          manager=self.request.user)
        return Response(data=serializers.BookingSerializer(bookings, many=True).data,
                        status=status.HTTP_200_OK)


class BookingsMonthGeneral(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, month, year, *args, **kwargs):
        target_start_date, target_end_date = utils.get_target_dates(month, year)
        bookings = Booking.objects.filter(check_in_date__lt=target_end_date, check_in_date__gte=target_start_date)
        context_bookings = []
        for booking in bookings:
            context_bookings.append(booking)
            temp_booking = copy(booking)
            initial_date = booking.check_in_date
            days_between = utils.days_between(initial_date, booking.check_out_date - datetime.timedelta(days=1))
            for x in range(days_between):
                temp_booking.check_in_date = temp_booking.check_in_date + datetime.timedelta(days=1)
                new_temp = copy(temp_booking)
                context_bookings.append(new_temp)
        return Response(data=serializers.BookingSerializer(context_bookings, many=True).data,
                        status=status.HTTP_200_OK)


class BookingInvoice(View):

    def get(self, request, pk):
        print(f"INSIDE VIEW {pk}")
        booking = Booking.objects.get(pk=pk)
        rooms = []
        iteration = 0
        parent_dict = {}
        category = Category.objects.all()
        for cat in category:
            parent_dict[cat.name] = 0
        # parent_dict['Total'] = 0

        for room in booking.rooms.all():
            parent_dict[room.category.name] += 1
            # parent_dict['Total'] += 1

        advance = 0
        for key in parent_dict:
            if parent_dict[key] <= 0:
                # del parent_dict[key]
                continue
            advance += parent_dict[key] * 10000
            rooms.append({
                'name': key,
                'rooms': parent_dict[key],
                'margin_top': 600 + (iteration * 20),
            })
            iteration += 1
        nights = utils.days_between(booking.check_in_date, booking.check_out_date)

        booking_payments = BookingPayment.objects.filter(booking=booking)
        context_payments = []
        for booking_payment in booking_payments:
            import datetime
            date_time = datetime.datetime.fromtimestamp(booking_payment.payment_date_time // 1000)
            context_payments.append(
                {
                    "amount": booking_payment.payment,
                    "payment_date_time": date_time,
                }
            )
        context = {
            'booking': booking,
            'booking_payments': context_payments,
            'rooms': rooms,
            'advance': advance,
            'cost_per_night': booking.total_cost_of_bookings,
            'nights': nights,
            'total_cost': booking.total_cost_of_bookings * nights,
        }
        return render(request, template_name='api/pdf_invoice.html', context=context)


"""
TODO:

Total cost per night
x Number of days

= Total 

"""
