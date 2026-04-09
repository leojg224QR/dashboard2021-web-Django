from django.contrib import admin

# Register your models here.
from .models import Venta, DetalleVenta 
class DetalleVentaInline(admin.TabularInline): 
    model = DetalleVenta 
    extra = 1 

@admin.register(Venta) 
class VentaAdmin(admin.ModelAdmin): 
    list_display = ('folio', 'fecha', 'cliente', 'sucursal', 'vendedor', 'metodo_pago', 'total') 
    inlines = [DetalleVentaInline]

@admin.register(DetalleVenta) 
class DetalleVentaAdmin(admin.ModelAdmin): 
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'importe')