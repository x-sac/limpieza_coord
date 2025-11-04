# 🗺️ Limpiador Automático de Coordenadas Geográficas

Script de Python para automatizar la limpieza y corrección de coordenadas geográficas en archivos Excel/CSV, especialmente diseñado para datos con errores comunes de captura.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Pandas](https://img.shields.io/badge/pandas-required-green.svg)](https://pandas.pydata.org/)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Problemas que Resuelve](#-problemas-que-resuelve)
- [Instalación](#-instalación)
- [Uso Rápido](#-uso-rápido)
- [Ejemplos](#-ejemplos)
- [Resultados](#-resultados)
- [Integración con QGIS](#️-integración-con-qgis)
- [Licencia](#-licencia)

## ✨ Características

- 🔄 **Detección automática de coordenadas invertidas** (X ↔ Y)
- 🔢 **Procesamiento de múltiples formatos**: símbolos de grado (°), comas, dos puntos
- 📊 **Manejo inteligente de separadores**: distingue entre comas decimales y separadores de miles
- 🌍 **Validación de rangos geográficos**: específico para México (configurable)
- 📝 **Manejo de coordenadas vacías**: mantiene NaN correctamente
- 💾 **Generación dual**: archivos Excel (.xlsx) y CSV (.csv)
- 📈 **Reportes detallados**: estadísticas y ejemplos de correcciones
- ⚡ **Alto rendimiento**: procesa cientos de registros en segundos

## 🎯 Problemas que Resuelve

### Errores Comunes Detectados:

| Error Original | Corrección | Ejemplo |
|---------------|------------|---------|
| Coordenadas invertidas | X ↔ Y | `X=20.5, Y=-97.7` → `X=-97.7, Y=20.5` |
| Símbolos de grado | Eliminar ° | `20.465°` → `20.465` |
| Comas como miles | Quitar comas | `20,738,059` → `20.738059` |
| Números sin decimales | Agregar punto | `20154103` → `20.154103` |
| Formato DMS | Extraer valor | `20:25:30°` → `20.25` |
| Múltiples coordenadas | Promediar | `Inicio: 20.5 Fin: 20.8` → `20.65` |

## 🚀 Instalación

### Requisitos

- Python 3.7 o superior
- pandas
- openpyxl (para archivos .xlsx)
- xlrd (para archivos .xls)

### Instalación de dependencias

```bash
pip install pandas openpyxl xlrd
```

## 📖 Uso Rápido

### Opción 1: Script Simple (Recomendado)

1. Descarga `ejecutar_limpieza_CSV.py`
2. Edita el nombre de tu archivo:
   ```python
   ARCHIVO_ENTRADA = "tu_archivo.xlsx"
   COLUMNA_X = 'x'  # Nombre de tu columna X
   COLUMNA_Y = 'y'  # Nombre de tu columna Y
   ```
3. Ejecuta:
   ```bash
   python ejecutar_limpieza_CSV.py
   ```

### Opción 2: Importar como Módulo

```python
from limpieza_coordenadas_v3_CSV import limpiar_coordenadas_excel

# Procesar archivo
df_limpio = limpiar_coordenadas_excel(
    archivo_entrada="datos_sucios.xlsx",
    archivo_salida="datos_limpios.xlsx",
    columna_x='longitud',
    columna_y='latitud'
)

# Genera automáticamente:
# - datos_limpios.xlsx (Excel)
# - datos_limpios.csv (CSV para QGIS)
```

### Opción 3: Usar la Clase Directamente

```python
from limpieza_coordenadas_v3_CSV import LimpiadorCoordenadas

# Crear instancia
limpiador = LimpiadorCoordenadas("datos_sucios.xlsx")

# Cargar datos
limpiador.cargar_datos()

# Procesar
limpiador.procesar_dataframe(columna_x='x', columna_y='y')

# Ver reporte
limpiador.generar_reporte()

# Guardar resultados
limpiador.guardar_resultado("datos_limpios.xlsx")
```

## 💡 Ejemplos

### Ejemplo 1: Coordenadas Invertidas

```python
# Entrada:
# X: 20.465061  (Esto es latitud, no longitud!)
# Y: -97.713375 (Esto es longitud, no latitud!)

# Salida:
# X_corregida: -97.713375  (Longitud)
# Y_corregida: 20.465061   (Latitud)
# Invertidas: TRUE
```

### Ejemplo 2: Comas como Separadores de Miles

```python
# Entrada:
# X: 20,738,059
# Y: -97,905,169

# Salida:
# X_corregida: -97.905169
# Y_corregida: 20.738059
```

### Ejemplo 3: Formato Complejo

```python
# Entrada:
# X: "Inicio: 20.242181° Fin: 20.279182°"
# Y: "Inicio: -98.209220° Fin: -98.150557°"

# Salida:
# X_corregida: -98.179889  (Promedio de longitudes)
# Y_corregida: 20.260182   (Promedio de latitudes)
```

## 📊 Resultados

El script genera archivos con las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| `x`, `y` | Coordenadas originales (sin modificar) |
| `X_original`, `Y_original` | Backup de valores originales |
| `X_limpia`, `Y_limpia` | Después de limpieza básica |
| **`X_corregida`** | **Coordenada X final (usar esta)** |
| **`Y_corregida`** | **Coordenada Y final (usar esta)** |
| `Invertidas` | TRUE si fueron invertidas automáticamente |

### Ejemplo de Reporte

```
   Resultados:
   Total de registros: 739
   Coordenadas limpias: 683 (92.4%)
   Coordenadas invertidas corregidas: 677
   Coordenadas vacías (mantenidas): 46
   Errores/No procesables: 10
```

## 🗺️ Integración con QGIS

Los archivos generados están listos para usar en QGIS:

### Importar en QGIS:

1. **Capa → Agregar capa → Agregar capa de texto delimitado**
2. Selecciona el archivo CSV generado
3. Configuración:
   - **Campo X**: `X_corregida`
   - **Campo Y**: `Y_corregida`
   - **SRC**: `EPSG:4326` (WGS 84)
4. Click en **Agregar**

### Sistema de Coordenadas

```
EPSG:4326 (WGS 84)
- Tipo: Geográfico
- Unidades: Grados decimales
- X (Longitud): -180° a 180°
- Y (Latitud): -90° a 90°
```

## 🔧 Configuración Avanzada

### Cambiar Rangos de Validación

Para trabajar con otras regiones, edita `limpieza_coordenadas_v3_CSV.py`:

```python
def validar_rango_coordenadas(self, x, y):
    # Rangos para México (default):
    lat_min, lat_max = 14, 33
    lon_min, lon_max = -118, -86
    
    # Cámbialo por tu región:
    # lat_min, lat_max = TU_LAT_MIN, TU_LAT_MAX
    # lon_min, lon_max = TU_LON_MIN, TU_LON_MAX
```
```

## 🧪 Testing

### Verificar Instalación

```python
import pandas as pd
print("Pandas instalado correctamente")

from limpieza_coordenadas_v3_CSV import limpiar_coordenadas_excel
print("Script cargado correctamente")
```

### Probar con Datos de Ejemplo

```python
# Crear datos de prueba
import pandas as pd

data = {
    'x': [20.5, '20,738,058', '20.5°', None],
    'y': [-97.7, '-97,905,199', '-97.7°', None]
}
df = pd.DataFrame(data)
df.to_excel('test.xlsx', index=False)

# Limpiar
from limpieza_coordenadas_v3_CSV import limpiar_coordenadas_excel
limpiar_coordenadas_excel('test.xlsx', 'test_limpio.xlsx', 'x', 'y')
```

## 📝 Changelog

### v3.0 (Actual)
- ✅ Generación automática de archivos CSV
- ✅ Manejo inteligente de comas (decimales vs. miles)
- ✅ Mejor manejo de coordenadas vacías
- ✅ Detección mejorada de formatos complejos

### v2.0
- ✅ Detección y corrección de coordenadas invertidas
- ✅ Procesamiento de múltiples formatos
- ✅ Reportes detallados

### v1.0
- ✅ Limpieza básica de coordenadas
- ✅ Eliminación de símbolos

## 🐛 Solución de Problemas

### Error: "KeyError: 'D'"
**Causa**: El nombre de las columnas no coincide.  
**Solución**: Verifica el nombre exacto de tus columnas y úsalo en el script.

```python
# Ver nombres de columnas
import pandas as pd
df = pd.read_excel("tu_archivo.xlsx")
print(df.columns)
```

### Error: "No module named 'pandas'"
**Solución**: Instala las dependencias.

```bash
pip install pandas openpyxl xlrd
```

### Los puntos aparecen en el lugar equivocado
**Causa**: Posiblemente usaste columnas originales en vez de las corregidas.  
**Solución**: En QGIS usa `X_corregida` y `Y_corregida`.

## 📈 Casos de Uso

- ✅ Limpieza de datos de campo (GPS, tablets)
- ✅ Migración de sistemas legacy
- ✅ Corrección de errores de captura manual
- ✅ Preparación de datos para análisis GIS
- ✅ Validación de bases de datos geoespaciales

## 🎓 Referencias

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [QGIS Documentation](https://docs.qgis.org/)
- [EPSG Codes](https://epsg.io/)
- [Coordinate Systems](https://en.wikipedia.org/wiki/Geographic_coordinate_system)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## 🙏 Agradecimientos

- A toda la gente que no sabe levantar coords y me hicieron estresarme para crear esto

---

⭐ **Si este proyecto te fue útil, considera darle una estrella en GitHub!**

📧 **¿Preguntas o sugerencias?** manda DM a Instagram: @sacxflores o X: @x__Sac__x.
