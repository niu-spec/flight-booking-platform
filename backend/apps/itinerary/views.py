from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.itinerary.models import Itinerary
from apps.itinerary.serializers import ItinerarySerializer


class ItineraryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItinerarySerializer
    
    def get_queryset(self):
        return Itinerary.objects.filter(user=self.request.user)


class ItineraryDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItinerarySerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        return Itinerary.objects.filter(user=self.request.user)


class ItineraryRefreshView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, itinerary_id):
        try:
            itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
            itinerary.refresh_status()
            
            return Response({
                'message': '行程状态已刷新',
                'itinerary': ItinerarySerializer(itinerary).data
            })
        except Itinerary.DoesNotExist:
            return Response({'error': '行程不存在'}, status=404)
