from django.http import JsonResponse
from .forms import PropertyForm

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from .models import Property
from .serializers import PropertiesListSerializer
from useraccount.models import User


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def properties_list(request):
    properties = Property.objects.all()
    serializer = PropertiesListSerializer(properties, many=True)
    return JsonResponse({"data": serializer.data})


@api_view(["POST", "FILES"])
def create_property(request):
    form = PropertyForm(request.POST, request.FILES)

    if form.is_valid():
        property = form.save(commit=False)
        property.landlord = request.user
        property.save()

        return JsonResponse({"success": True})
    else:
        print("error", form.errors, form.non_field_errors)
        return JsonResponse({"errors": form.errors.as_json()}, status=400)