import os
import requests
import pandas as pd

pais_iso2 = {"spain": "ES", "brazil": "BR", "mexico": "MX", "usa": "US",
             "colombia": "CO", "italy": "IT", "japan": "JP", "germany": "DE", "china": "CN"}

inicio = 2010
fin = 2025

def obtencion_de_inflacion_por_pais(iso2, inicio):
    """
    ESTA FUNCION PERMITE DESCARGAR UN CSV CON LA INFLACION POR AÑO PARA EL PAIS CON EL IDENTIFICADOR ISO2 DADO
    """

    #ESTRUCTURAMOS LA URL COMO LO NECESITA LA API DEL WORLDBANK PARA RECUPERAR EL ONJETO JSON CON LOS DATOS DE INFLACION
    url = f"https://api.worldbank.org/v2/country/{iso2}/indicator/FP.CPI.TOTL.ZG"

    response = requests.get(url, {'format':'json'})
    response.raise_for_status()
    datos = response.json() #[metadatos, lista de diccionarios: [{...., 'date':YYYY, 'value':inflacion anual}]]

    #SCRAPEAMOS LOS DATOS DE INFLACION POR AÑO HASTA LLEGAR A AÑOS INFERIORES AL PERIODO ANALIZADO
    pre_pandas = []
    periodo = True
    cont = 0
    while periodo:
        #TOMAMOS UNICAMENTE LOS DATOS QUE NOS INTERESAN DEL JSON
        pre_pandas.append({'date':datos[1][cont]['date'], 'inf_anual':datos[1][cont]['value'], 'pais':datos[1][cont]['country']['value']})
        cont += 1
        periodo = int(datos[1][cont]['date']) >=  inicio

    df = pd.DataFrame(pre_pandas)

    #CONVERTIMOS LOS TIPOS DE DATOS A SUS ADECUADOS
    df["date"] = pd.to_datetime(df["date"], errors = 'coerce')
    df["inf_anual"] = pd.to_numeric(df["inf_anual"], errors = 'coerce')

    #ELIMINAMOS LAS FILAS CON AÑO O DATO DE INFLACION FALTANTES
    df = df.dropna(subset = ["date", "inf_anual"])

    return df


for pais, iso2 in pais_iso2.items():
    try:
        df = obtencion_de_inflacion_por_pais(iso2, inicio)
        #DESCARGAMOS UN ARCHIVO CSV CON EL HISTORICO DE INFLACION
        directorio_guardado = os.path.join('..', 'datos', 'inflacion', f"inflacion_anual_{pais}.csv")
        df.to_csv(directorio_guardado, index = False)
        print(f"LOS DATOS DE INFLACION DE {pais} SE DESCARGARON CORRECTAMENTE")
        print(f"\n\n\n{df}\n\n\n")

    except requests.exceptions.HTTPError as e:
        print(f"HUBO PROBLEMAS CON LA CONSULTA DE LOS DATOS DE {pais}")
    except Exception as e:
        print(f"HUBO UN PROBLEMA CON LOS DATOS DE {pais} QUE NO ES DEL SCRAPPING: {e}")

