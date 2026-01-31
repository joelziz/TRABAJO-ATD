import requests
import pandas as pd
import os

PAISES = {"spain": "ESP", "brazil": "BRA", "mexico": "MEX", "usa": "USA", 
          "colombia": "COL", "italy": "ITA", "japan": "JPN", "germany": "DEU", "china": "CHN"}

INDICADORES = {
    'CC.EST': 'Control of Corruption',
    'GE.EST': 'Government Effectiveness',
    'PV.EST': 'Political Stability',
    'RQ.EST': 'Regulatory Quality',
    'RL.EST': 'Rule of Law',
    'VA.EST': 'Voice and Accountability'}

def descargar_indicador(pais_codigo, indicador_codigo):
    #DESCARGA UNO DE LOS INDICADORES PARA UN PAIS
    url = f"https://api.worldbank.org/v2/country/{pais_codigo}/indicator/{indicador_codigo}"
    params = {'format': 'json', 'date': "2010:2023", 'per_page':500}
    
    #DEVOLVEMOS LA LISTA DE JSONS QUE DEVUELVE LA CONSULTA
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data[1]


total = len(PAISES) * len(INDICADORES)
contador = 0

for pais_nombre, pais_codigo in PAISES.items():
    wgi = []
    riesgo = 0
    for ind_codigo, ind_nombre in INDICADORES.items():
        contador += 1
        print(f"Descargando {contador}/{total}: {pais_nombre} - {ind_nombre}...")
        
        #SE GUARDA EL SCRAPPING
        datos = descargar_indicador(pais_codigo, ind_codigo)
        
        indice = 0
        for registro in datos:
            #SE EXTRAE EL VALOR DEL INDICADOR ESPECIFICO EN EL AÑO ESPECIFICO EN EL PAIS ESPECIFICO
            wgi.append({'pais':pais_nombre, 'anyo': registro['date'], 'indicaor': ind_nombre, 'valor': registro['value']})
    
    #GUARDAMOS LOS DATOS DE TODOS LOS INDICADORES EN CADA AÑO POR PAIS
    df = pd.DataFrame(wgi)        
    df.to_csv(os.path.join('..', 'datos', 'wgis', f"wgi_riesgo_{pais_nombre}.csv"), index=False)