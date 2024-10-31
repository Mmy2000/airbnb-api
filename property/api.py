from amadeus import NotFoundError
from django.http import JsonResponse
from .forms import PropertyForm , PropertyImages
from .serializers import PropertiesDetailSerializer , ReservationsListSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .amadeus_client import get_amadeus_client
from amadeus import Client, ResponseError
import datetime
from django.conf import settings

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from .models import Property , Reservation
from .serializers import PropertiesListSerializer
from useraccount.models import User
from rest_framework_simplejwt.tokens import AccessToken
import logging
from django.views.decorators.http import require_GET
import requests

# Set up logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def properties_list(request):

    try:
        token = request.META["HTTP_AUTHORIZATION"].split("Bearer ")[1]
        token = AccessToken(token)
        user_id = token.payload["user_id"]
        user = User.objects.get(pk=user_id)
    except Exception as e:
        user = None

    favorites = []
    properties = Property.objects.all()
    landlord_id = request.GET.get("landlord_id", "")
    is_favorites = request.GET.get("is_favorites","")
    country = request.GET.get("country", "")
    city = request.GET.get("city", "")
    category = request.GET.get("category", "")
    checkin_date = request.GET.get("checkIn", "")
    checkout_date = request.GET.get("checkOut", "")
    bedrooms = request.GET.get("numBedrooms", "")
    guests = request.GET.get("numGuests", "")
    bathrooms = request.GET.get("numBathrooms", "")

    if checkin_date and checkout_date:
        exact_matches = Reservation.objects.filter(
            start_date=checkin_date
        ) | Reservation.objects.filter(end_date=checkout_date)
        overlap_matches = Reservation.objects.filter(
            start_date__lte=checkout_date, end_date__gte=checkin_date
        )
        all_matches = []

        for reservation in exact_matches | overlap_matches:
            all_matches.append(reservation.property_id)

        properties = properties.exclude(id__in=all_matches)

    if landlord_id:
        properties = properties.filter(landlord_id=landlord_id)

    if is_favorites:
        properties = properties.filter(favorited__in=[user])

    if guests:
        properties = properties.filter(guests__gte=guests)

    if bedrooms:
        properties = properties.filter(bedrooms__gte=bedrooms)

    if bathrooms:
        properties = properties.filter(bathrooms__gte=bathrooms)

    if country:
        properties = properties.filter(country=country)

    if city:
        properties = properties.filter(city=city)

    if category and category != "undefined":
        properties = properties.filter(category=category)

    if user:
        for property in properties:
            if user in property.favorited.all():
                favorites.append(property.id)
    serializer = PropertiesListSerializer(properties, many=True)
    return JsonResponse({"data": serializer.data, "favorites": favorites})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def properties_detail(request, pk):
    property = Property.objects.get(pk=pk)

    serializer = PropertiesDetailSerializer(property, many=False)

    return JsonResponse(serializer.data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def property_reservations(request, pk):
    property = Property.objects.get(pk=pk)
    reservations = property.reservations.all()

    serializer = ReservationsListSerializer(reservations, many=True)

    return JsonResponse(serializer.data, safe=False)


@api_view(["POST"])
def create_property(request):
    property_form = PropertyForm(request.POST, request.FILES)

    if property_form.is_valid():
        property_instance = property_form.save(commit=False)
        property_instance.landlord = request.user
        property_instance.save()

        # Handle multiple images
        images = request.FILES.getlist("property_images")
        for image in images:
            property_image = PropertyImages(property=property_instance, image=image)
            property_image.save()

        return JsonResponse({"success": True},status=200)

    else:
        print("error", property_form.errors, property_form.non_field_errors)
        return JsonResponse({"errors": property_form.errors.as_json()}, status=400)


@api_view(["PUT"])
def edit_property(request, property_id):
    try:
        # Get the property instance
        property_instance = Property.objects.get(id=property_id, landlord=request.user)

        # Update property details
        property_form = PropertyForm(
            request.POST, request.FILES, instance=property_instance
        )

        if property_form.is_valid():
            property_form.save()

            # Handle new images if provided
            if "property_images" in request.FILES:
                # Clear previous images if needed (optional)
                PropertyImages.objects.filter(property=property_instance).delete()

                images = request.FILES.getlist("property_images")
                for image in images:
                    property_image = PropertyImages(
                        property=property_instance, image=image
                    )
                    property_image.save()

            return JsonResponse(
                {"success": True, "message": "Property updated successfully"}
            )
        else:
            return JsonResponse({"errors": property_form.errors.as_json()}, status=400)
    except Property.DoesNotExist:
        return JsonResponse(
            {"error": "Property not found or you are not authorized to edit it"},
            status=404,
        )


@api_view(["DELETE"])
def delete_property(request, property_id):
    try:
        # Get the property instance
        property_instance = Property.objects.get(id=property_id, landlord=request.user)

        # Delete associated property images
        property_instance.property_images.all().delete()

        # Delete the property itself
        property_instance.delete()

        return JsonResponse(
            {"success": True, "message": "Property deleted successfully"}
        )
    except Property.DoesNotExist:
        return JsonResponse(
            {"error": "Property not found or you are not authorized to delete it"},
            status=404,
        )


@api_view(["POST"])
def book_property(request, pk):
    try:
        start_date = request.POST.get("start_date", "")
        end_date = request.POST.get("end_date", "")
        number_of_nights = request.POST.get("number_of_nights", "")
        total_price = request.POST.get("total_price", "")
        guests = request.POST.get("guests", "")

        property = Property.objects.get(pk=pk)

        Reservation.objects.create(
            property=property,
            start_date=start_date,
            end_date=end_date,
            number_of_nights=number_of_nights,
            total_price=total_price,
            guests=guests,
            created_by=request.user,
        )

        return JsonResponse({"success": True})
    except Exception as e:
        print("Error", e)

        return JsonResponse({"success": False})


@api_view(["DELETE"])
def cancel_reservation(request, pk):
    try:
        # Fetch the reservation based on the provided primary key (pk)
        reservation = Reservation.objects.get(pk=pk)

        # Optionally, you can check if the reservation was created by the current user
        if reservation.created_by != request.user:
            return JsonResponse(
                {
                    "success": False,
                    "error": "You do not have permission to cancel this reservation.",
                },
                status=403,
            )

        # Delete the reservation
        reservation.delete()

        return JsonResponse({"success": True})

    except Reservation.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Reservation not found."}, status=404
        )
    except Exception as e:
        print("Error:", e)
        return JsonResponse({"success": False, "error": str(e)})


@api_view(["POST"])
def toggle_favorite(request, pk):
    property = Property.objects.get(pk=pk)

    if request.user in property.favorited.all():
        property.favorited.remove(request.user)

        return JsonResponse({"is_favorite": False})
    else:
        property.favorited.add(request.user)

        return JsonResponse({"is_favorite": True})


amadeus = Client(
    client_id=settings.AMADEUS_CLIENT_ID, client_secret=settings.AMADEUS_CLIENT_SECRET
)


def search_flights(request):
    # Get parameters from the request
    origin = request.GET.get("origin")
    destination = request.GET.get("destination")
    departure_date = request.GET.get("departure_date")
    adults = request.GET.get("adults", 1)  # default to 1 adult if not specified
    print(amadeus.client_id,amadeus.client_secret)

    # Validate required parameters
    if not origin or not destination or not departure_date:
        return JsonResponse(
            {
                "error": "Please provide origin, destination, and departure_date parameters."
            },
            status=400,
        )

    try:
        # Call Amadeus API with the provided parameters
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=int(adults),
        ).data
        return JsonResponse(response, safe=False)
    except ResponseError as error:
        return JsonResponse({"error": str(error)}, status=500)


# @require_GET  # Ensure the endpoint only responds to GET requests
# def hotel_search(request):
#     # Get parameters from the request
#     city_code = request.GET.get("city_code")
#     check_in_date = request.GET.get("check_in_date")
#     check_out_date = request.GET.get("check_out_date")
#     adults = request.GET.get("adults", 1)  # Default to 1 adult if not specified

#     # Validate required parameters

#     # if not city_code or not check_in_date or not check_out_date:
#     #     return JsonResponse(
#     #         {
#     #             "error": "Please provide city_code, check_in_date, and check_out_date parameters."
#     #         },
#     #         status=400,
#     #     )

#     try:
#         # Call Amadeus API with the provided parameters
#         print("before response")
#         response = amadeus.shopping.hotel_offers.get(
#             hotelIds="RTPAR001",
#             cityCode=city_code,
#             checkInDate=check_in_date,
#             checkOutDate=check_out_date,
#             adults=int(adults),
#         ).data
#         print("after response")

#         # Return the response as JSON
#         return JsonResponse(response, safe=False)
#     except ResponseError as error:
#         logger.error(f"Amadeus API error: {error}")
#         return JsonResponse(
#             {
#                 "error": "An error occurred with the Amadeus API. Check your parameters and try again."
#             },
#             status=500,
#         )
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#         return JsonResponse(
#             {"error": "An unexpected error occurred. Please try again later."},
#             status=500,
#         )


def hotel_search(request):
    # Get parameters from the request
    city_code = request.GET.get("city_code")
    check_in_date = request.GET.get("check_in_date")
    check_out_date = request.GET.get("check_out_date")
    adults = request.GET.get("adults", 1)  # Default to 1 adult if not specified
    room_quantity = request.GET.get("room_quantity", 1)  # Default to 1 room
    payment_policy = request.GET.get("payment_policy", "NONE")  # Default payment policy
    best_rate_only = request.GET.get("best_rate_only", "true")  # Default to true

    # Validate required parameters
    if not city_code or not check_in_date or not check_out_date:
        return JsonResponse(
            {
                "error": "Please provide city_code, check_in_date, and check_out_date parameters."
            },
            status=400,
        )

    try:
        # Construct the API URL
        api_url = (
            f"https://test.api.amadeus.com/v3/shopping/hotel-offers?"
            f"hotelIds=RTPAR001&adults={adults}&checkInDate={check_in_date}"
            f"&checkOutDate={check_out_date}&roomQuantity={room_quantity}"
            f"&paymentPolicy={payment_policy}&bestRateOnly={best_rate_only}"
        )

        # Make the request to the Amadeus API
        response = requests.get(
            api_url, headers={"Authorization": f"Bearer jYPNASmwnh4LYkKKdAfsqoxAal0g"}
        )
        response_data = response.json()  # Parse JSON response

        # Check if the response is successful
        if response.status_code == 200:
            # Return the response as JSON
            return JsonResponse(response_data, safe=False)
        else:
            # Handle API error response
            logger.error(f"Amadeus API error: {response_data}")
            return JsonResponse(
                {
                    "error": "An error occurred with the Amadeus API. Check your parameters and try again."
                },
                status=response.status_code,
            )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JsonResponse(
            {"error": "An unexpected error occurred. Please try again later."},
            status=500,
        )

