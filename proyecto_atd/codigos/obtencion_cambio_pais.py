import pandas as pd
import os
import time
import random

#  PAISES Y MONEDAS (ISO 4217)
paises_monedas = {
    "Brazil": "BRL", 
    "China": "CNY",
    "Colombia": "COP",
    "Germany": "EUR",
    "Italy": "EUR",
    "Spain": "EUR",
    "Japan": "JPY",
    "Mexico": "MXN"
}

# LAS URL INCLUYEN COMO PARAMETROS LA FECHA EN LA QUE SE QUIERE BUSCAR PERO NO LOS PAISES
# POR ESO, LAS BUSQUEDAS SE HACEN POR AÑOS

for anyo in range(2010, 2025):
        time.sleep(random.uniform(1, 2))
        tablas = pd.read_html(f"https://www.xe.com/es-es/currencytables/?from=USD&date={anyo}-12-31")
        df = tablas[0]

          
        # HACEMOS EL PROCESAMIENTO POR PAIS
        for pais, moneda in paises_monedas.items():
            if moneda in df['Moneda'].values:
                #EXTRAEMOS EL CAMBIO EN EL AÑO Y LA MONEDA BUSCADOS
                cambio_val = df.loc[df['Moneda'] == moneda].loc[:, 'Unidades por USD'].iloc[0]
                cambio_val = float(str(cambio_val).replace(',', '.'))
                
                #DFINIMOS LA RUTA DE SALIDA
                ruta_salida = os.path.join('..', 'datos', 'cambios', f"cambio_{pais.lower()}.csv") 
                
                #CREAMOS EL NUEVO REGISTRO Y LO AGREGAMOS AL ARCHIVO CSV
                nuevo_registro = {"fecha": f"{anyo}-12-31", "cambio": cambio_val, "pais": pais}
        
                try:
                    df_pais = pd.read_csv(ruta_salida)
                    df_pais = pd.concat([df_pais, pd.DataFrame([nuevo_registro])], ignore_index=True)
                except FileNotFoundError:
                    df_pais = pd.DataFrame([nuevo_registro])
                
                df_pais = df_pais.sort_values("fecha")

                df_pais.to_csv(ruta_salida, index=False)     

"""
for pais in paises_monedas:
    df_pais = pd.read_csv(os.path.join('..', 'datos', 'pre_proceso', 'cambios', f"cambio_{pais.lower()}.csv"))
    print(df_pais)
"""