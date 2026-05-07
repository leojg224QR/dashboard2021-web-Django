from datetime import datetime, timedelta 
from django.db.models import Sum, Count, Max, F, Avg
from django.db.models.functions import TruncMonth 
from django.http import HttpResponse 
from django.shortcuts import render 
from openpyxl import Workbook 
import pandas as pd
from scipy import stats
from ventas.models import DetalleVenta
import json 
 
from ventas.models import Venta, DetalleVenta
from catalogos.models import Cliente, Vendedor,Categoria, MetodoPago
 
 
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

def analitica_avanzada(request):
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    moneda_activa = request.GET.get('moneda', 'MXN')
    
    vendedores_seleccionados = request.GET.getlist('vendedores')
    categorias_seleccionadas = request.GET.getlist('categorias')
    # NUEVOS FILTROS
    clientes_seleccionados = request.GET.getlist('clientes')
    metodos_seleccionados = request.GET.getlist('metodos_pago')

    # Tasa de cambio con EURO incluido
    if moneda_activa == 'USD':
        tasa_cambio = 18.50
    elif moneda_activa == 'EUR':
        tasa_cambio = 20.50 # Puedes ajustar este valor
    else:
        tasa_cambio = 1.0

    # --- 2. CONSTRUIR DICCIONARIOS DE FILTROS ---
    filtros_venta = {}
    filtros_detalle = {}

    if fecha_inicio:
        filtros_venta['fecha__gte'] = fecha_inicio
        filtros_detalle['venta__fecha__gte'] = fecha_inicio
    if fecha_fin:
        filtros_venta['fecha__lte'] = fecha_fin
        filtros_detalle['venta__fecha__lte'] = fecha_fin
    if vendedores_seleccionados:
        filtros_venta['vendedor__id__in'] = vendedores_seleccionados
        filtros_detalle['venta__vendedor__id__in'] = vendedores_seleccionados
    if categorias_seleccionadas:
        filtros_detalle['producto__categoria__id__in'] = categorias_seleccionadas
    if clientes_seleccionados:
        filtros_venta['cliente__id__in'] = clientes_seleccionados
        filtros_detalle['venta__cliente__id__in'] = clientes_seleccionados
    if metodos_seleccionados:
        filtros_venta['metodo_pago__id__in'] = metodos_seleccionados
        filtros_detalle['venta__metodo_pago__id__in'] = metodos_seleccionados

    # --- 3. APLICAR FILTROS A LA BASE DE DATOS ---
    ventas_qs = Venta.objects.filter(**filtros_venta)
    detalles_qs = DetalleVenta.objects.filter(**filtros_detalle).select_related('producto__categoria')

    # --- 4. KPIs CON CONVERSIÓN DE MONEDA ---
    kpis_raw = ventas_qs.aggregate(
        ventas_analizadas=Count('id'),
        monto_total=Sum('total'),
        promedio=Avg('total'),
        maximo=Max('total')
    )
    
    # Aplicamos la división de la tasa de cambio
    kpis = {
        'ventas_analizadas': kpis_raw['ventas_analizadas'] or 0,
        'monto_total': float(kpis_raw['monto_total'] or 0) / tasa_cambio,
        'promedio': float(kpis_raw['promedio'] or 0) / tasa_cambio,
        'maximo': float(kpis_raw['maximo'] or 0) / tasa_cambio,
    }

    # --- 5. TABLAS TOP CON CONVERSIÓN ---
    top_vendedores = list(ventas_qs.values('vendedor__nombre').annotate(
        total_vendido=Sum('total')
    ).order_by('-total_vendido')[:5])
    for tv in top_vendedores: tv['total_vendido'] = float(tv['total_vendido']) / tasa_cambio

    top_sucursales = list(ventas_qs.values('sucursal__nombre').annotate(
        total_vendido=Sum('total')
    ).order_by('-total_vendido')[:5])
    for ts in top_sucursales: ts['total_vendido'] = float(ts['total_vendido']) / tasa_cambio

    # --- 6. GRÁFICA TENDENCIA CON CONVERSIÓN ---
    ventas_mes = ventas_qs.annotate(mes=TruncMonth('fecha')).values('mes').annotate(
        total_mes=Sum('total')
    ).order_by('mes')

    labels_tendencia = [v['mes'].strftime('%Y-%m') for v in ventas_mes] if ventas_mes else []
    data_tendencia = [(float(v['total_mes']) / tasa_cambio) for v in ventas_mes] if ventas_mes else []

    # --- 7. ANOVA (SOLO SOBRE LOS DATOS FILTRADOS) ---
    df = pd.DataFrame(list(detalles_qs.values('producto__categoria__nombre', 'importe')))
    f_stat, p_value, grupos_count, mensaje_anova = 0, 1, 0, "No hay datos suficientes con estos filtros."

    if not df.empty:
        df['importe'] = df['importe'].astype(float) / tasa_cambio # También convertimos el importe
        if len(df['producto__categoria__nombre'].unique()) > 1:
            grupos = [grupo['importe'].values for nombre, grupo in df.groupby('producto__categoria__nombre')]
            f_stat, p_value = stats.f_oneway(*grupos)
            grupos_count = len(grupos)
            if p_value < 0.05:
                mensaje_anova = "Diferencias significativas detectadas entre las categorías filtradas."
            else:
                mensaje_anova = "No se detectan diferencias significativas en esta muestra."

    # --- 8. PREPARAR LISTAS PARA LOS SELECTORES DEL HTML ---
    cat_vendedores = Vendedor.objects.all()
    cat_categorias = Categoria.objects.all()
    cat_clientes = Cliente.objects.all() 
    cat_metodos = MetodoPago.objects.all() 

    # Listas de proyección
    proyeccion_categoria = list(detalles_qs.values('producto__categoria__nombre').annotate(
        total_proyectado=Sum('importe')
    ).order_by('-total_proyectado'))
    for pc in proyeccion_categoria: pc['total_proyectado'] = float(pc['total_proyectado'] or 0) / tasa_cambio

    proyeccion_metodo = list(ventas_qs.values('metodo_pago__nombre').annotate(
        total_proyectado=Sum('total')
    ).order_by('-total_proyectado'))
    for pm in proyeccion_metodo: pm['total_proyectado'] = float(pm['total_proyectado'] or 0) / tasa_cambio

    # Extraer a los líderes para los textos dinámicos
    insight_vendedor = top_vendedores[0] if top_vendedores else None
    insight_categoria = proyeccion_categoria[0] if proyeccion_categoria else None
    insight_metodo = proyeccion_metodo[0] if proyeccion_metodo else None
    
    # Cliente estrella
    top_cliente = ventas_qs.values('cliente__nombre').annotate(total=Sum('total')).order_by('-total').first()
    insight_cliente_nombre = top_cliente['cliente__nombre'] if top_cliente else None
    insight_cliente_total = (float(top_cliente['total'] or 0) / tasa_cambio) if top_cliente else 0

    # Mes estrella
    insight_mes = max(ventas_mes, key=lambda x: x['total_mes'])['mes'] if ventas_mes else None

    context = {
        'kpis': kpis,
        'top_vendedores': top_vendedores,
        'top_sucursales': top_sucursales,
        'labels_tendencia': json.dumps(labels_tendencia),
        'data_tendencia': json.dumps(data_tendencia),
        'anova_f_stat': f"{f_stat:.4f}" if pd.notna(f_stat) else "N/A",
        'anova_p_value': f"{p_value:.6f}" if pd.notna(p_value) else "N/A",
        'anova_grupos': grupos_count,
        'anova_mensaje': mensaje_anova,
        
        # Filtros y Catálogos para el HTML
        'moneda_activa': moneda_activa,
        'cat_vendedores': cat_vendedores,
        'cat_categorias': cat_categorias,
        'cat_clientes': cat_clientes, 
        'cat_metodos': cat_metodos, 
        'proyeccion_categoria': proyeccion_categoria,
        'proyeccion_metodo': proyeccion_metodo,
        'insight_vendedor': insight_vendedor,
        'insight_categoria': insight_categoria,
        'insight_metodo': insight_metodo,
        'insight_cliente_nombre': insight_cliente_nombre,
        'insight_cliente_total': insight_cliente_total,
        'insight_mes': insight_mes,
    }
    
    
    return render(request, 'dashboard/analitica_avanzada.html', context)


def exportar_ventas_excel(request):
    # 1. Extraemos los datos de la base de datos
    # Usamos select_related para que la consulta sea súper rápida
    ventas = Venta.objects.select_related('cliente', 'sucursal', 'vendedor', 'metodo_pago').all()
    
    # 2. Armamos una lista de diccionarios con el formato exacto para Excel
    datos_excel = []
    for v in ventas:
        datos_excel.append({
            'Folio': v.folio,
            'Fecha': v.fecha.strftime('%Y-%m-%d') if v.fecha else 'S/F',
            'Cliente': v.cliente.nombre if v.cliente else 'Público en general',
            'Sucursal': v.sucursal.nombre if v.sucursal else 'N/A',
            'Vendedor': v.vendedor.nombre if v.vendedor else 'N/A',
            'Método de Pago': v.metodo_pago.nombre if v.metodo_pago else 'N/A',
            'Total (MXN)': float(v.total) if v.total else 0.0
        })
        
    # 3. Convertimos los datos a un DataFrame de Pandas
    df = pd.DataFrame(datos_excel)
    
    # 4. Preparamos la respuesta HTTP para que el navegador sepa que es un archivo descargable
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    # Le ponemos un nombre profesional y dinámico al archivo (ej: Reporte_Ventas_20260502.xlsx)
    fecha_hoy = datetime.now().strftime("%Y%m%d")
    response['Content-Disposition'] = f'attachment; filename="Reporte_Ventas_{fecha_hoy}.xlsx"'
    
    # 5. Escribimos el DataFrame en el archivo Excel de salida
    df.to_excel(response, index=False, engine='openpyxl')
    
    return response