from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from inventory.models import Product, Sale
from inventory.api.v1.sererializers.ProductSerializer import ProductSerializer
from inventory.api.v1.sererializers.SaleSerializer import SaleSerializer, SaleDetailSerializer

class ProductViewSet(mixins.ListModelMixin, 
                    mixins.CreateModelMixin, 
                    viewsets.GenericViewSet):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SaleViewSet(mixins.ListModelMixin,
                mixins.CreateModelMixin, 
                viewsets.GenericViewSet):
    
    queryset = Sale.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SaleDetailSerializer
        return SaleSerializer

