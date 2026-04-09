from datetime import datetime, timedelta 
from django.db.models import Sum, Count, Max, F 
from django.db.models.functions import TruncMonth 
from django.http import HttpResponse 
from django.shortcuts import render 
from openpyxl import Workbook 
import json 
 
from ventas.models import Venta, DetalleVenta 
from catalogos.models import Cliente, Vendedor 
 
 
def inicio(request): 
    ventas = Venta.objects.select_related( 
        'cliente', 'vendedor', 'metodo_pago', 'sucursal' 
    ).all() 
 
    fecha_inicio = request.GET.get('fecha_inicio') 
    fecha_fin = request.GET.get('fecha_fin') 
    cliente_id = request.GET.get('cliente') 
    vendedor_id = request.GET.get('vendedor') 
 
    if fecha_inicio: 
        ventas = ventas.filter(fecha__gte=datetime.strptime(fecha_inicio, '%Y-%m-%d').date()) 
 
    if fecha_fin: 
        ventas = ventas.filter(fecha__lte=datetime.strptime(fecha_fin, '%Y-%m-%d').date()) 
 
    if cliente_id:  
        ventas = ventas.filter(cliente_id=cliente_id) 
 
    if vendedor_id: 
        ventas = ventas.filter(vendedor_id=vendedor_id) 
 
    total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0 
    total_documentos = ventas.count() 
    ticket_promedio = total_ventas / total_documentos if total_documentos > 0 else 0 
    venta_maxima = ventas.aggregate(maximo=Max('total'))['maximo'] or 0
    metodos_usados = ventas.values('metodo_pago__nombre').distinct().count() 
 
    detalles = DetalleVenta.objects.filter(venta__in=ventas) 
 
    total_productos_vendidos = detalles.aggregate(total=Sum('cantidad'))['total'] or 0 
 
    ventas_por_metodo = list( 
        ventas.values('metodo_pago__nombre') 
        .annotate(total=Sum('total')) 
        .order_by('-total') 
    ) 
 
    ventas_por_vendedor = list( 
        ventas.values('vendedor__nombre') 
        .annotate(total=Sum('total')) 
        .order_by('-total') 
    ) 
 
    productos_mas_vendidos = list( 
        detalles.values('producto__nombre') 
        .annotate(total_cantidad=Sum('cantidad')) 
        .order_by('-total_cantidad')[:10] 
    ) 
 
    ventas_por_categoria = list( 
        detalles.values('producto__categoria__nombre') 
        .annotate(total_importe=Sum('importe')) 
        .order_by('-total_importe') 
    ) 
 
    clientes = Cliente.objects.all() 
    vendedores = Vendedor.objects.all() 
 
    contexto = { 
        'total_ventas': total_ventas, 
        'total_documentos': total_documentos, 
        'ticket_promedio': ticket_promedio, 
        'venta_maxima': venta_maxima, 
        'total_productos_vendidos': total_productos_vendidos, 
        'metodos_usados': metodos_usados, 
        'clientes': clientes, 
        'vendedores': vendedores, 
        'ventas_por_metodo_json': json.dumps(ventas_por_metodo, default=str), 
        'ventas_por_vendedor_json': json.dumps(ventas_por_vendedor, default=str), 
        'productos_mas_vendidos_json': json.dumps(productos_mas_vendidos, default=str), 
        'ventas_por_categoria_json': json.dumps(ventas_por_categoria, default=str), 
        'fecha_inicio': fecha_inicio or '', 
        'fecha_fin': fecha_fin or '', 
        'cliente_id': cliente_id or '', 
        'vendedor_id': vendedor_id or '', 
    } 
 
    return render(request, 'dashboard/inicio.html', contexto) 
 
 
def reporte_mensual(request): 
    datos = ( 
        Venta.objects.annotate(mes=TruncMonth('fecha')) 
        .values('mes') 
        .annotate( 
            total_ventas=Sum('total'), 
            total_documentos=Count('id') 
        ) 
        .order_by('mes') 
    ) 
    return render(request, 'dashboard/reporte_mensual.html', {'datos': datos}) 
 
 
def exportar_ventas_excel(request): 
    ventas = Venta.objects.select_related('cliente', 'sucursal', 'vendedor', 'metodo_pago').all() 
 
    wb = Workbook() 
    ws = wb.active 
    ws.title = 'Ventas' 
 
    ws.append([ 
        'Folio', 'Fecha', 'Cliente', 'Sucursal', 
        'Vendedor', 'Método de Pago', 'Subtotal', 'Impuesto', 'Total' 
    ]) 
 
    for v in ventas: 
        ws.append([ 
            v.folio, 
            str(v.fecha), 
            v.cliente.nombre, 
            v.sucursal.nombre, 
            v.vendedor.nombre, 
            v.metodo_pago.nombre, 
            float(v.subtotal), 
            float(v.impuesto), 
            float(v.total), 
        ]) 
 
    response = HttpResponse( content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 
    response['Content-Disposition'] = 'attachment; filename=ventas.xlsx' 
    wb.save(response) 
    return response 
 
 
def dashboard_comparativo(request): 
    comparativo_categorias = ( 
        DetalleVenta.objects.values('producto__categoria__nombre') 
        .annotate(total=Sum('importe')) 
        .order_by('-total') 
    ) 
 
    comparativo_ciudades = ( 
        Venta.objects.values('sucursal__ciudad') 
        .annotate(total=Sum('total')) 
        .order_by('-total') 
    ) 
 
    comparativo_metodos = ( 
        Venta.objects.values('metodo_pago__nombre') 
        .annotate(total=Sum('total')) 
        .order_by('-total') 
    ) 
 
    return render(request, 'dashboard/comparativo.html', { 
        'comparativo_categorias': comparativo_categorias, 
        'comparativo_ciudades': comparativo_ciudades, 
        'comparativo_metodos': comparativo_metodos, 
    }) 