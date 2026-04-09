from django.contrib import admin

# Register your models here.
from .models import Categoria, Sucursal, MetodoPago, Cliente, Vendedor, Producto 
admin.site.register(Categoria) 
admin.site.register(Sucursal) 
admin.site.register(MetodoPago) 
admin.site.register(Cliente) 
admin.site.register(Vendedor) 
admin.site.register(Producto)
