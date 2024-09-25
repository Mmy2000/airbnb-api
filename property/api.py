from django.http import JsonResponse
from .forms import PropertyForm , PropertyImages
from .serializers import PropertiesDetailSerializer , ReservationsListSerializer

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from .models import Property , Reservation
from .serializers import PropertiesListSerializer
from useraccount.models import User
from rest_framework_simplejwt.tokens import AccessToken


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
    if landlord_id:
        properties = properties.filter(landlord_id=landlord_id)

    if is_favorites:
        properties = properties.filter(favorited__in=[user])

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

        return JsonResponse({"success": True})

    else:
        print("error", property_form.errors, property_form.non_field_errors)
        return JsonResponse({"errors": property_form.errors.as_json()}, status=400)


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


@api_view(["POST"])
def toggle_favorite(request, pk):
    property = Property.objects.get(pk=pk)

    if request.user in property.favorited.all():
        property.favorited.remove(request.user)

        return JsonResponse({"is_favorite": False})
    else:
        property.favorited.add(request.user)

        return JsonResponse({"is_favorite": True})
