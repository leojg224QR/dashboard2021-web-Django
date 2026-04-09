from django.urls import path 
from .views import ( 
    lista_categorias, 
    lista_clientes, 
    lista_productos, 
    lista_sucursales, 
    lista_vendedores, 
    lista_metodos_pago 
) 
 
urlpatterns = [ 
    path('categorias/', lista_categorias, name='lista_categorias'), 
    path('clientes/', lista_clientes, name='lista_clientes'), 
    path('productos/', lista_productos, name='lista_productos'), 
    path('sucursales/', lista_sucursales, name='lista_sucursales'), 
    path('vendedores/', lista_vendedores, name='lista_vendedores'), 
    path('metodos_pago/', lista_metodos_pago, name='lista_metodos_pago'), 
]