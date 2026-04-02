from rest_framework import generics, permissions, response # type: ignore
from service.utils.product_matching import product_matching_service
from service.views.products_views import get_all_products_cached # type: ignore
from service.models import NotificationProduct # type: ignore
from service.serializers.notification_prod import NotificationProductSerializer # type: ignore
from rest_framework import status # type: ignore
from django.core.cache import cache # type: ignore
from service.utils.fetch_mysql_data import DB_Query # type: ignore

class NotificationProductListCreateView(generics.ListCreateAPIView):
    queryset = NotificationProduct.objects.all()
    serializer_class = NotificationProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)