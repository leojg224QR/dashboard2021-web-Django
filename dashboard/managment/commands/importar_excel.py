import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from catalogos.models import Cliente, Vendedor, Sucursal, MetodoPago, Producto, Categoria
from ventas.models import Venta, DetalleVenta
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa datos desde DashBoard2021.xlsx a la base de datos'

    def handle(self, *args, **kwargs):
        ruta_excel = os.path.join(settings.BASE_DIR, 'DashBoard2021.xlsx')
        
        if not os.path.exists(ruta_excel):
            self.stdout.write(self.style.ERROR(f'No se encontró el archivo: {ruta_excel}'))
            return

        self.stdout.write(self.style.SUCCESS('Leyendo el archivo Excel...'))
        
        try:
            # Leemos el excel
            df = pd.read_excel(ruta_excel)
            
            # Reemplazamos los valores nulos (NaN) con None o strings vacíos
            df = df.fillna('')

            for index, fila in df.iterrows():
                # 1. Crear o recuperar los catálogos (Ajusta los nombres de las columnas del df según tu Excel)
                
                # Ejemplo: Si tu columna en Excel se llama 'Nombre Cliente'
                cliente, _ = Cliente.objects.get_or_create(
                    nombre=fila['Nombre Cliente'] # <--- CAMBIA ESTO POR EL NOMBRE DE TU COLUMNA REAL
                )
                
                vendedor, _ = Vendedor.objects.get_or_create(
                    nombre=fila['Vendedor'] # <--- CAMBIA ESTO
                )
                
                sucursal, _ = Sucursal.objects.get_or_create(
                    nombre=fila['Sucursal'], # <--- CAMBIA ESTO
                    ciudad=fila['Ciudad']    # <--- CAMBIA ESTO
                )
                
                metodo_pago, _ = MetodoPago.objects.get_or_create(
                    nombre=fila['Método de Pago'] # <--- CAMBIA ESTO
                )

                # 2. Crear la Venta
                # Asumiendo que tu modelo Venta tiene estos campos
                venta, venta_creada = Venta.objects.get_or_create(
                    folio=fila['Folio'], # Usamos el folio como identificador único
                    defaults={
                        'fecha': fila['Fecha'], 
                        'cliente': cliente,
                        'vendedor': vendedor,
                        'sucursal': sucursal,
                        'metodo_pago': metodo_pago,
                        'subtotal': fila['Subtotal'],
                        'impuesto': fila['Impuesto'],
                        'total': fila['Total']
                    }
                )

                # 3. Solo si la venta es nueva, le agregamos el detalle (Producto)
                if venta_creada:
                    categoria, _ = Categoria.objects.get_or_create(nombre=fila['Categoria'])
                    
                    producto, _ = Producto.objects.get_or_create(
                        nombre=fila['Producto'],
                        defaults={'categoria': categoria, 'precio': fila['Precio']}
                    )
                    
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=fila['Cantidad'],
                        importe=fila['Importe']
                    )

            self.stdout.write(self.style.SUCCESS('¡Importación completada con éxito!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la importación: {str(e)}'))