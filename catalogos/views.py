from django.shortcuts import render

# Create your views here.
from .models import Categoria, Cliente, Producto, Sucursal, Vendedor, MetodoPago 
def lista_categorias(request): 
    categorias = Categoria.objects.all() 
    return render(request, 'catalogos/lista_categorias.html', {'categorias': 
    categorias}) 

def lista_clientes(request): 
    clientes = Cliente.objects.all() 
    return render(request, 'catalogos/lista_clientes.html', {'clientes': clientes}) 

def lista_productos(request): 
    productos = Producto.objects.select_related('categoria').all() 
    return render(request, 'catalogos/lista_productos.html', {'productos': productos})
 
def lista_sucursales(request): 
    sucursales = Sucursal.objects.all() 
    return render(request, 'catalogos/lista_sucursales.html', {'sucursales': 
    sucursales}) 

def lista_vendedores(request): 
    vendedores = Vendedor.objects.select_related('sucursal').all() 
    return render(request, 'catalogos/lista_vendedores.html', {'vendedores': 
    vendedores}) 

def lista_metodos_pago(request): 
    metodos = MetodoPago.objects.all() 
    return render(request, 'catalogos/lista_metodos_pago.html', {'metodos': 
    metodos})