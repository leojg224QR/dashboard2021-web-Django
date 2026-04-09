from django.db import models

# Create your models here.
class Categoria(models.Model): 
    nombre = models.CharField(max_length=100) 
 
    def __str__(self): 
        return self.nombre

class Sucursal(models.Model): 
    nombre = models.CharField(max_length=100) 
    ciudad = models.CharField(max_length=100, blank=True, null=True) 
    estado = models.CharField(max_length=100, blank=True, null=True) 
    pais = models.CharField(max_length=100, blank=True, null=True) 
 
    def __str__(self): 
        return f"{self.nombre} - {self.ciudad}"

class MetodoPago(models.Model): 
    nombre = models.CharField(max_length=100) 
 
    def __str__(self): 
        return self.nombre 
 
 
class Cliente(models.Model): 
    nombre = models.CharField(max_length=150) 
 
    def __str__(self): 
        return self.nombre 
 
 
class Vendedor(models.Model): 
    nombre = models.CharField(max_length=150) 
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE) 
 
    def __str__(self): 
        return self.nombre 
 
class Producto(models.Model): 
    codigo = models.CharField(max_length=50) 
    nombre = models.CharField(max_length=150) 
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE) 
    precio = models.DecimalField(max_digits=12, decimal_places=2, default=0) 
def __str__(self): 
    return f"{self.codigo} - {self.nombre}"


