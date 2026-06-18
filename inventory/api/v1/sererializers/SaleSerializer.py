from rest_framework import serializers
from inventory.models import Sale
from .ProductSerializer import ProductSerializer

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            'id',
            'product', 
            'quantity', 
            'price_unity_retail', 
            'price_unity_wholesale'
            ]
        
        read_only_fields = [
                            'id',
                            'criado_em'
                            ]

class SaleDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado para listagem e exibição (Read).
    Traz os dados do produto aninhados.
    """
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'product', 'quantity', 'price_unity_retail', 'price_unity_wholesale']