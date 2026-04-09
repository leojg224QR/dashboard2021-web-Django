from django.db import models

# Create your models here.
from catalogos.models import Cliente, Sucursal, Vendedor, MetodoPago, Producto 
class Venta(models.Model): 
    folio = models.CharField(max_length=50, unique=True) 
    fecha = models.DateField() 
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE) 
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE) 
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE) 
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE) 
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0) 
    impuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0) 
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
     
def __str__(self): 
    return f"{self.folio} - {self.fecha}" 

class DetalleVenta(models.Model): 
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, 
    related_name='detalles') 
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE) 
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=0) 
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0) 
    importe = models.DecimalField(max_digits=12, decimal_places=2, default=0) 

def __str__(self): 
    return f"{self.venta.folio} - {self.producto.nombre}"