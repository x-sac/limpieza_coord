import pandas as pd
import re
import numpy as np

class LimpiadorCoordenadas:
    """
    Clase para limpiar y validar coordenadas geográficas en archivos Excel
    """
    
    def __init__(self, archivo_entrada):
        """
        Inicializa el limpiador con el archivo de entrada
        
        Args:
            archivo_entrada: Ruta al archivo Excel con coordenadas sucias
        """
        self.archivo_entrada = archivo_entrada
        self.df = None
        self.df_limpio = None
        
    def cargar_datos(self):
        """Carga el archivo Excel"""
        try:
            self.df = pd.read_excel(self.archivo_entrada)
            print(f" Archivo cargado exitosamente: {len(self.df)} registros")
            return True
        except Exception as e:
            print(f" Error al cargar archivo: {e}")
            return False
    
    def limpiar_texto_basico(self, valor):
        """
        Limpieza básica: quita símbolos de grado, comas, espacios extras
        
        Args:
            valor: Valor de coordenada a limpiar
            
        Returns:
            Valor limpio como string
        """
        if pd.isna(valor):
            return None
            
        valor_str = str(valor).strip()
        
        # Si está vacío o es solo espacios, retornar None
        if not valor_str or valor_str == 'nan' or valor_str == '':
            return None
        
        # Manejar formato de rango "Inicio: X Fin: Y" - tomar el promedio
        if 'Inicio:' in valor_str and 'Fin:' in valor_str:
            try:
                inicio_match = re.search(r'Inicio:\s*([-\d.]+)', valor_str)
                fin_match = re.search(r'Fin:\s*([-\d.]+)', valor_str)
                if inicio_match and fin_match:
                    inicio = float(inicio_match.group(1))
                    fin = float(fin_match.group(1))
                    promedio = (inicio + fin) / 2
                    return str(promedio)
            except:
                pass
        
        # Quitar símbolos de grado (°)
        valor_str = valor_str.replace('°', '')
        
        # Detectar si las comas son separadores de miles o decimales
        num_comas = valor_str.count(',')
        
        if num_comas > 0:
            # Si hay punto Y comas, las comas son separadores de miles
            if '.' in valor_str:
                valor_str = valor_str.replace(',', '')
            # Si hay múltiples comas (ej: 20,738,059), son separadores de miles
            elif num_comas > 1:
                valor_str = valor_str.replace(',', '')
            # Si hay solo una coma y está en posición de decimal (últimos 3 dígitos o menos)
            elif num_comas == 1:
                partes = valor_str.split(',')
                # Si la parte después de la coma tiene 3+ dígitos, es separador de miles
                if len(partes) == 2 and len(partes[1]) >= 3:
                    valor_str = valor_str.replace(',', '')
                else:
                    # Es separador decimal
                    valor_str = valor_str.replace(',', '.')
        
        # Quitar espacios
        valor_str = valor_str.strip()
        
        # Quitar caracteres no numéricos excepto punto, menos y dos puntos
        valor_str = re.sub(r'[^\d.\-:]', '', valor_str)
        
        # Si después de limpiar queda vacío, retornar None
        if not valor_str or valor_str == '.':
            return None
        
        return valor_str
    
    def extraer_de_formato_dms(self, valor):
        """
        Extrae coordenadas del formato con dos puntos (DMS)
        Ejemplo: "19:25:30" -> 19.25
        
        Args:
            valor: String con formato DMS
            
        Returns:
            Valor numérico o None
        """
        if ':' in str(valor):
            try:
                partes = str(valor).split(':')
                if len(partes) >= 2:
                    # Extraer la parte entre el primer : y antes del °
                    resultado = float(partes[1].split('°')[0])
                    return resultado
            except:
                pass
        return None
    
    def aplicar_formato_excel(self, valor):
        """
        Aplica la lógica de las fórmulas de Excel:
        =SI(D2<0,IZQUIERDA(D2,3)&"."&DERECHA(D2,LARGO(D2)-3),IZQUIERDA(D2,2)&"."&DERECHA(D2,LARGO(D2)-2))
        
        Args:
            valor: Valor numérico o string de coordenada
            
        Returns:
            Valor formateado correctamente
        """
        try:
            valor_num = float(valor)
            valor_str = str(valor).replace('.', '').replace('-', '')
            
            if valor_num < 0:
                # Negativo: tomar 3 caracteres + punto + resto
                if len(valor_str) >= 3:
                    resultado = '-' + valor_str[:2] + '.' + valor_str[2:]
                else:
                    resultado = valor_num
            else:
                # Positivo: tomar 2 caracteres + punto + resto
                if len(valor_str) >= 2:
                    resultado = valor_str[:2] + '.' + valor_str[2:]
                else:
                    resultado = valor_num
            
            return float(resultado)
        except:
            return None
    
    def verificar_division_necesaria(self, valor):
        """
        Verifica si el valor necesita ser dividido (coordenadas muy largas)
        
        Args:
            valor: Valor numérico de coordenada
            
        Returns:
            Valor corregido
        """
        try:
            valor_num = float(valor)
            
            # Contar dígitos antes del punto decimal
            valor_abs = abs(valor_num)
            
            # Si la coordenada es demasiado grande (sin decimales correctos)
            if valor_abs > 10000000:  # Más de 7 dígitos
                # Probablemente le faltan decimales: 20154103 -> 20.154103
                valor_str = str(int(valor_abs))
                if len(valor_str) >= 8:
                    # Tomar los primeros 2 dígitos como entero, resto como decimal
                    resultado = float(valor_str[:2] + '.' + valor_str[2:])
                    return resultado if valor_num >= 0 else -resultado
                return valor_num / 1000000
            elif valor_abs > 1000000:
                return valor_num / 1000000
            elif valor_abs > 100000:
                return valor_num / 100000
            elif valor_abs > 10000:
                return valor_num / 10000
            elif valor_abs > 1000:
                # Podría ser 20154 -> 20.154
                valor_str = str(int(valor_abs))
                if len(valor_str) >= 5:
                    resultado = float(valor_str[:2] + '.' + valor_str[2:])
                    return resultado if valor_num >= 0 else -resultado
                return valor_num / 1000
            
            return valor_num
        except:
            return None
    
    def validar_rango_coordenadas(self, x, y):
        """
        Valida que las coordenadas estén en rangos válidos para México
        y detecta si están invertidas
        
        Args:
            x: Coordenada X (longitud)
            y: Coordenada Y (latitud)
            
        Returns:
            (x_corregida, y_corregida, invertidas)
        """
        try:
            x_num = float(x)
            y_num = float(y)
            
            # Rangos aproximados para México:
            # Latitud: 14° a 33° N
            # Longitud: -86° a -118° W (negativas)
            
            lat_min, lat_max = 14, 33
            lon_min, lon_max = -118, -86
            
            # Verificar si están en el rango correcto
            x_en_rango_lon = lon_min <= x_num <= lon_max
            y_en_rango_lat = lat_min <= y_num <= lat_max
            
            x_en_rango_lat = lat_min <= x_num <= lat_max
            y_en_rango_lon = lon_min <= y_num <= lon_max
            
            invertidas = False
            
            # Si X está en rango de latitud y Y en rango de longitud, están invertidas
            if x_en_rango_lat and y_en_rango_lon and not (x_en_rango_lon and y_en_rango_lat):
                invertidas = True
                return y_num, x_num, invertidas
            
            return x_num, y_num, invertidas
            
        except:
            return x, y, False
    
    def limpiar_coordenada(self, valor, es_x=True):
        """
        Pipeline completo de limpieza para una coordenada
        
        Args:
            valor: Valor de coordenada a limpiar
            es_x: True si es coordenada X (longitud), False si es Y (latitud)
            
        Returns:
            Valor limpio o None si no se pudo limpiar
        """
        if pd.isna(valor):
            return None
        
        # Paso 1: Limpieza básica
        valor_limpio = self.limpiar_texto_basico(valor)
        
        if not valor_limpio:
            return None
        
        # Paso 2: Intentar extraer de formato DMS si tiene ":"
        if ':' in valor_limpio:
            valor_dms = self.extraer_de_formato_dms(valor_limpio)
            if valor_dms is not None:
                valor_limpio = str(valor_dms)
        
        # Paso 3: Aplicar formato de Excel
        valor_formateado = self.aplicar_formato_excel(valor_limpio)
        
        if valor_formateado is None:
            try:
                valor_formateado = float(valor_limpio)
            except:
                return None
        
        # Paso 4: Verificar si necesita división
        valor_final = self.verificar_division_necesaria(valor_formateado)
        
        return valor_final
    
    def procesar_dataframe(self, columna_x='D', columna_y='E'):
        """
        Procesa todo el DataFrame limpiando las coordenadas
        
        Args:
            columna_x: Nombre de la columna con coordenadas X
            columna_y: Nombre de la columna con coordenadas Y
        """
        if self.df is None:
            print("✗ Primero debes cargar los datos")
            return
        
        self.df_limpio = self.df.copy()
        
        print("\n Procesando coordenadas...")
        
        # Limpiar coordenadas X e Y
        self.df_limpio['X_limpia'] = self.df[columna_x].apply(lambda x: self.limpiar_coordenada(x, es_x=True))
        self.df_limpio['Y_limpia'] = self.df[columna_y].apply(lambda x: self.limpiar_coordenada(x, es_x=False))
        
        # Validar y corregir inversiones
        resultados = self.df_limpio.apply(
            lambda row: self.validar_rango_coordenadas(row['X_limpia'], row['Y_limpia']),
            axis=1
        )
        
        self.df_limpio['X_corregida'] = resultados.apply(lambda x: x[0] if x else None)
        self.df_limpio['Y_corregida'] = resultados.apply(lambda x: x[1] if x else None)
        self.df_limpio['Invertidas'] = resultados.apply(lambda x: x[2] if x else False)
        
        # Crear columnas con coordenadas originales para comparación
        self.df_limpio['X_original'] = self.df[columna_x]
        self.df_limpio['Y_original'] = self.df[columna_y]
        
        # Estadísticas
        total = len(self.df_limpio)
        validas = self.df_limpio['X_corregida'].notna().sum()
        invertidas = self.df_limpio['Invertidas'].sum()
        
        print(f"\nResultados:")
        print(f"   Total de registros: {total}")
        print(f"   Coordenadas limpias: {validas} ({validas/total*100:.1f}%)")
        print(f"   Coordenadas invertidas corregidas: {invertidas}")
        print(f"   Errores/No procesables: {total - validas}")
    
    def guardar_resultado(self, archivo_salida):
        """
        Guarda el DataFrame limpio en un nuevo archivo Excel Y CSV
        
        Args:
            archivo_salida: Ruta del archivo de salida (se generarán .xlsx y .csv)
        """
        if self.df_limpio is None:
            print(" Primero debes procesar el DataFrame")
            return
        
        try:
            # Guardar como Excel
            self.df_limpio.to_excel(archivo_salida, index=False)
            print(f"\n Archivo Excel guardado: {archivo_salida}")
            
            # Guardar como CSV (cambiar extensión)
            archivo_csv = archivo_salida.rsplit('.', 1)[0] + '.csv'
            self.df_limpio.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
            print(f" Archivo CSV guardado: {archivo_csv}")
            print(f"\n Usa el archivo CSV para QGIS: {archivo_csv}")
            
        except Exception as e:
            print(f"\n✗ Error al guardar archivo: {e}")
    
    def generar_reporte(self):
        """Genera un reporte detallado de los cambios realizados"""
        if self.df_limpio is None:
            print("✗ Primero debes procesar el DataFrame")
            return
        
        print("\n" + "="*60)
        print("REPORTE DE LIMPIEZA DE COORDENADAS")
        print("="*60)
        
        # Mostrar algunos ejemplos de cambios
        cambios = self.df_limpio[
            (self.df_limpio['X_original'].astype(str) != self.df_limpio['X_corregida'].astype(str)) |
            (self.df_limpio['Y_original'].astype(str) != self.df_limpio['Y_corregida'].astype(str))
        ].head(10)
        
        if len(cambios) > 0:
            print("\nEjemplos de cambios realizados:")
            for idx, row in cambios.iterrows():
                print(f"\nRegistro {idx + 1}:")
                print(f"   X: {row['X_original']} → {row['X_corregida']}")
                print(f"   Y: {row['Y_original']} → {row['Y_corregida']}")
                if row['Invertidas']:
                    print(f"Coordenadas invertidas y corregidas")
        
        # Registros con problemas
        problemas = self.df_limpio[
            self.df_limpio['X_corregida'].isna() | self.df_limpio['Y_corregida'].isna()
        ]
        
        if len(problemas) > 0:
            print(f"\n{len(problemas)} registros con problemas que requieren revisión manual")


# Función principal de uso fácil
def limpiar_coordenadas_excel(archivo_entrada, archivo_salida=None, columna_x='D', columna_y='E'):
    """
    Función principal para limpiar coordenadas de un archivo Excel
    
    Args:
        archivo_entrada: Ruta al archivo Excel con coordenadas sucias
        archivo_salida: Ruta para guardar el archivo limpio (opcional)
        columna_x: Nombre de la columna con coordenadas X (default: 'D')
        columna_y: Nombre de la columna con coordenadas Y (default: 'E')
    
    Returns:
        DataFrame con coordenadas limpias
    """
    # Crear instancia del limpiador
    limpiador = LimpiadorCoordenadas(archivo_entrada)
    
    # Cargar datos
    if not limpiador.cargar_datos():
        return None
    
    # Procesar
    limpiador.procesar_dataframe(columna_x, columna_y)
    
    # Generar reporte
    limpiador.generar_reporte()
    
    # Guardar si se especificó archivo de salida
    if archivo_salida:
        limpiador.guardar_resultado(archivo_salida)
    
    return limpiador.df_limpio


# Ejemplo de uso
if __name__ == "__main__":
    # Usar el script
    archivo_entrada = "afectaciones_sucio_0311.xlsx"
    archivo_salida = "afectaciones_limpio_0311.xlsx"
    
    print("Iniciando limpieza de coordenadas...")
    print("="*60)
    
    df_limpio = limpiar_coordenadas_excel(
        archivo_entrada=archivo_entrada,
        archivo_salida=archivo_salida,
        columna_x='x',  # Columna X
        columna_y='y'   # Columna Y
    )
    
    if df_limpio is not None:
        print("\nProceso completado exitosamente!")
        print(f"\nPuedes encontrar el archivo limpio en: {archivo_salida}")
    else:
        print("\nHubo un error en el proceso")