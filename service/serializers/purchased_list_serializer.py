from rest_framework import serializers # type: ignore
from service.models import SaveToPuchase, Shopping
from service.utils.product_matching import product_matching_service
from service.views.products_views import get_all_products_cached # type: ignore


class PurchasedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopping
        fields = ['id', 'user', 'product_id', 'is_shopping', 'is_purchased']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.full_name if instance.user else None

        products = get_all_products_cached()
        product = next((p for p in products if p.get('id') == instance.product_id), None)

        representation['product_name'] = product.get('name') if product else None
        representation['product_price'] = product.get('price') if product else None
        return representation


class BulkPurchaseSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of product IDs to mark as purchased"
    )

    def validate_product_ids(self, value):
        if not value:
            raise serializers.ValidationError("Product IDs list cannot be empty.")
        return value
    
    
class TotalPurchasePrice(PurchasedListSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta(PurchasedListSerializer.Meta):
        fields = PurchasedListSerializer.Meta.fields + ['total_price']

    def get_total_price(self, obj):
        products = get_all_products_cached()
        total = 0
        for item in obj:
            product = next((p for p in products if p.get('id') == item.product_id), None)
            if product and product.get('price') is not None:
                total += product.get('price')
        return total
    
    
class SaveToPuchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaveToPuchase
        fields = ['id', 'user', 'product_id']
        read_only_fields = ['id', 'user']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.full_name if instance.user else None

        products = get_all_products_cached()
        product = next((p for p in products if p.get('id') == instance.product_id), None)

        representation['product_name'] = product.get('name') if product else None
        representation['product_price'] = product.get('price') if product else None
        representation['unit_amount'] = product.get('unit_amount') if product else None
        representation['price_per_unit'] = product.get('price_per_unit') if product else None
        representation['supermarket_id'] = product.get('supermarket_id') if product else None
        representation['image_url'] = product.get('image_url') if product else None
        
        # product matching 
        product_matching_ids = product_matching_service(
            product_id=product.get('id'),
            supermarket_id=product.get('supermarket_id')
        )        
        matching_products = [
            {
                'id': p.get('id'),
                'name': p.get('name'),
                'price': p.get('price'),
                'supermarket_id': p.get('supermarket_id'),
            } for p in products if p.get('id') in product_matching_ids
        ]
                
        prices = [p['price'] for p in matching_products if p.get('price') is not None]

        representation['save_amount'] = max(prices) - min(prices) if prices else None
        
        return representation