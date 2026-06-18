from rest_framework import serializers
from inventory.models import Product

class ProductSerializer(serializers.ModelSerializer):
    imagem = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Product
        fields = [
                'id',
                'name',
                'description',
                'imagem'
                ]
        read_only_fields = ['id', 'criado_em']
        
        

    