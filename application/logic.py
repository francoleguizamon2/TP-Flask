from .models import RegistroClimatico
from statistics import mean

def obtener_estadisticas():
    registros = RegistroClimatico.query.all()
    temperaturas = [r.temperatura for r in registros]
    precipitaciones = [r.precipitacion for r in registros]

    return {
        'promedio_temp': round(mean(temperaturas), 2),
        'max_temp': max(temperaturas),
        'min_temp': min(temperaturas),
        'promedio_prec': round(mean(precipitaciones), 2),
        'max_prec': max(precipitaciones),
        'min_prec': min(precipitaciones),
    }
