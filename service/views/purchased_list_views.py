from rest_framework import generics, permissions, response # type: ignore
from rest_framework.views import APIView #type: ignore
from rest_framework import status # type: ignore
from service.models import SaveToPuchase, Shopping # type: ignore
from service.serializers.purchased_list_serializer import PurchasedListSerializer, BulkPurchaseSerializer, SaveToPuchaseSerializer # type: ignore
from service.views.products_views import get_all_products_cached # type: ignore


class PurchasedListView(generics.ListCreateAPIView):
    queryset = Shopping.objects.all()
    serializer_class = PurchasedListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user, is_purchased=True)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BulkPurchaseSerializer
        return PurchasedListSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_ids = serializer.validated_data['product_ids']

        # Update shopping items for the current user
        updated_count = Shopping.objects.filter(
            user=request.user,
            product_id__in=product_ids
        ).update(
            is_shopping=False,
            is_purchased=True
        )

        return response.Response(
            {
                'message': f'Successfully updated {updated_count} products as purchased',
                'updated_count': updated_count,
                'product_ids': product_ids
            },
            status=status.HTTP_200_OK
        )



class PurchasedListDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BulkPurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_ids = serializer.validated_data['product_ids']

        # Delete shopping items for the current user
        deleted_count = Shopping.objects.filter(
            user=request.user,
            product_id__in=product_ids
        ).update(
            is_shopping=True,
            is_purchased=False
        )

        return response.Response(
            {
                'message': f'Successfully deleted {deleted_count} products from purchased list',
                'deleted_count': deleted_count,
                'product_ids': product_ids
            },
            status=status.HTTP_200_OK
        )
        
        
class TotalPurchasePriceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        purchased_items = Shopping.objects.filter(user=request.user, is_purchased=True)
        products = get_all_products_cached()

        total_price = 0
        for item in purchased_items:
            product = next((p for p in products if p.get('id') == item.product_id), None)
            if product and product.get('price') is not None:
                total_price += product.get('price')

        return response.Response({'total_price': total_price})



class SaveToPurchaseView(generics.ListCreateAPIView):
    queryset = SaveToPuchase.objects.all()
    serializer_class = SaveToPuchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    # Override create for custom response
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return response.Response({
            "message": "Product saved to purchase list successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    # total_save_amount
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        items = serializer.data

        # Calculate total save_amount
        total_save_amount = sum(item.get('save_amount', 0) or 0 for item in items)

        return response.Response({
            "items": items,
            "total_save_amount": total_save_amount
        })