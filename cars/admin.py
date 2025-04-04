from django.http import JsonResponse
from django.views import View
from .models import Car

class CarListView(View):
    def get(self, request):
        cars = list(Car.objects.values())
        return JsonResponse({"cars": cars}, safe=False)
