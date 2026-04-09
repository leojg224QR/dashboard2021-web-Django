from django.urls import path 
from .views import inicio, reporte_mensual, exportar_ventas_excel, dashboard_comparativo 
 
urlpatterns = [ 
    path('', inicio, name='inicio'), 
    path('reportes/mensual/', reporte_mensual, name='reporte_mensual'), 
    path('exportar/excel/', exportar_ventas_excel, name='exportar_ventas_excel'), 
    path('comparativo/', dashboard_comparativo, name='dashboard_comparativo'), 
]