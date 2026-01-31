import os
import requests
import pandas as pd
import csv

#DEFINIMOS UN DICCIONARIO CON LOS PAISES A ANALIZAR Y LA ETIQUETA DE SUS ETFS
pais_etf = {"spain": "ewp.us", "brazil": "ewz.us", "mexico": "eww.us", "usa": "spy.us", 
            "colombia": "colo.us", "italy": "ewi.us", "japan": "ewj.us", "germany": "ewg.us", "china": "mchi.us",}
#DEFINIMOS LA DIREECCION DENTRO DE NUESTRO DIRECTORIO EN EL QUE GUARDAR LOS RESULTADOS
directorio_de_guardado = os.path.join("..","datos", "precios") 
#DEFINIMOS LOS AÑOS LIMITE DEL PERIODO QUE ANALIZAREMOS
anio_inicio = 2010
anio_fin = 2025 

def buscador_etfs_diarios_stooq(etiqueta):
    """
    CON ESTA FUNCION ACCEDEMOS AL CSV QUE DA STOOQ SOBRE EL PRECIO HISTORICO DE LA ETF SELECCIONADA,
    MEDIANTE REQUESTS, LUEGO LO CONVERTIMOS EN UN DATA FRAME Y LO DEVOLVEMOS
    """

    url = "https://stooq.com/q/d/l/" #ESTA ES LA URL DEL 'DESCARGADOR' DE LOS CSV DE STOOQ

    #EL PARAMETRO S IDENTIFICA LA ETIQUETA MIENTRAS Q EL I EL INTERVALO (AL SER D ES POR DIA)
    response = requests.get(url, {"s":etiqueta, "i":"d"}) 
    response.raise_for_status() #SI HAY ERROR QUE LEVANTE UNA EXCEPCION QUE MANEJAREMOS FUERA DE LA FUNCION

    #PROCESAMOS EL CSV PARA PODER OBTENER UNA LISTA DE DICCIONARIOS DONDE CADA CLAVE ES LA COLUMNO Y EL VALOR SU RESPECTIVO VALOR
    lineas = response.text.splitlines()
    reader = csv.DictReader(lineas)
    filas = list(reader)

    #CREAMOS EL DATAFRAME Y NORMALIZAMOS LAS CABECERAS
    df = pd.DataFrame(filas)
    df.columns = [c.strip().lower() for c in df.columns]

    #TENEMOS QUE MANEJAR LOS TIPOS DE LOS DATOS YA QUE EL CSV LOS TOMA A TODOS COMO TEXTO
    #EN CASO DE QUE LA CONVERSION NO SEA POSIBLE SE DEJA EL VALOR EN NULO
    df["date"] = pd.to_datetime(df["date"], errors ='coerce')
    for resto in df.columns[1:]:
        df[resto] = pd.to_numeric(df[resto], errors = 'coerce')
    
    #QUITAMOS LAS FILAS CON FECHAS INVALIDAS/NULL Y LO ORDENAMOS POR FECHA
    df = df.dropna(subset=["date"]).sort_values("date")

    return(df)

def filtar_fechas(df, inicio, fin):
    #FILTRAMOS LAS FILAS DEL CSV QUE ESTEN DENTRO DEL PERIODO A ANALIZAR
    filas_dentro = (df["date"].dt.year >= inicio) & (df["date"].dt.year <= fin)
    df = df.loc[filas_dentro]

    return df

#DESCARGAMOS LOS DATOS PARA CADA PAIS
for pais, etiqueta in pais_etf.items():
    try:
        df = buscador_etfs_diarios_stooq(etiqueta)
        df = filtar_fechas(df, anio_inicio, anio_fin)
        
        salida_en = os.path.join(directorio_de_guardado, f"precio_etf_{pais}_{etiqueta.replace('.', '-')}.csv")
        df.to_csv(salida_en, index = False)
        print(f"LOS DATOS DE {pais} SE DESCARGARON EXITOSAMENTE")
        
    except requests.exceptions.HTTPError:
        print(f"NO SE PUDIERON DESCARGAR LOS DATOS DE {pais.upper()}")
    except Exception as e:
        print(f"HUBO UN PROBLEMA QUE NO TIENE QUE VER CON LA CONSULTA DE DATOS CON {pais.upper()}: {e}")