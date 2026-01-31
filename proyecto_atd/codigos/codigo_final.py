import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression

PAISES = [ 'usa', 'spain', 'colombia', 'brazil', 'italy', 
          'germany', 'japan', 'china', 'mexico']

direccion_datos = Path(__file__).parent.parent / "datos"

TICKERS = {'usa': 'spy', 'spain': 'ewp', 'colombia': 'colo', 'brazil': 'ewz', 'italy': 'ewi', 'germany': 'ewg',
           'japan': 'ewj', 'china': 'mchi', 'mexico': 'eww'}

def procesar_pais(pais):
    datos = {}

    #EL TIPO DE CAMBIO DE USA ES SSIEMPRE 1
    if pais == 'usa':
        fechas = pd.date_range('2010-12-31', '2023-12-31', freq='YE')
        cambio = pd.DataFrame({
            'fecha': fechas,
            'cambio': 1.0,
            'pais': 'USA',
            'anyo': fechas.year,    
        })
        datos['cambio'] = cambio
    else:
        #EL RESTO DE TIPOS DE CAMBIOS LO CONSULTAMOS DE LOS FICHEROS CSV CAMBIO_ANUAL
        cambio_path = direccion_datos / "cambios" / f"cambio_{pais}.csv"
        cambio = pd.read_csv(cambio_path)
        cambio['fecha'] = pd.to_datetime(cambio['fecha'])
        cambio['anyo'] = cambio['fecha'].dt.year
        datos['cambio'] = cambio[['fecha', 'anyo', 'cambio']]
    
    #ACCEDEMOS A LA INFLACION EN LOS FICHEROS CSV INFLACION_ANUAL
    inf_path = direccion_datos / "inflacion" / f"inflacion_anual_{pais}.csv"
    inf = pd.read_csv(inf_path)
    inf['date'] = pd.to_datetime(inf['date'])
    inf['anyo'] = inf['date'].dt.year
    datos['inflacion'] = inf[['anyo', 'inf_anual']]
    
    #ACCEDEDMOS A LOS PRECIOS DE LOS ETFS EN LOS FICHEROS CSV PRECIO_ETF
    ticker = TICKERS[pais]
    precio_path = direccion_datos / "precios" / f"precio_etf_{pais}_{ticker}-us.csv"
    precio = pd.read_csv(precio_path)
    precio['date'] = pd.to_datetime(precio['date'])
    precio['anyo'] = precio['date'].dt.year
    precio['mes'] = precio['date'].dt.month
    datos['precio'] = precio[['date', 'anyo', 'mes', 'close']]
    
    #ACCEDDEMOS A LOS WGIS EN LOS FICHEROS WGI_RIESGO
    wgi_path = direccion_datos / "wgis" / f"wgi_riesgo_{pais}.csv"
    wgi = pd.read_csv(wgi_path)
    wgi = wgi.rename(columns={'indicaor': 'indicador'})
    datos['wgi'] = wgi
    
    #DEVOLVEMOS UN DICCIONARIO DONDE CADA CLAVE SON EL TITULO DE LOS DATOS SCRAPPEADOS Y SU VALORES
    #SON OBJETOS DATAFRAME QUE SE CONSIGUEN AL LEER LOS ARCHIVOS CSV DE LOS DATOS
    return datos

def calcular_variacion_2011_2023(pais):
    #OBTENEMOS TODOS LOS DATOS DEL PAIS
    datos = procesar_pais(pais)

    #SEPARAMOS CADA DATAFRAME
    precio = datos['precio']
    wgi = datos['wgi']
    cambio = datos['cambio']
    inflacion = datos['inflacion']
    
    #CALCULAMOS EL PRECIO INICIAL Y FINAL DEL ETF
    precio_2011 = precio[(precio['anyo'] == 2011)].sort_values('date')
    precio_2011 = precio_2011.head(1)
    
    precio_2023 = precio[(precio['anyo'] == 2023)].sort_values('date')
    precio_2023 = precio_2023.tail(1)    
    
    close_2011 = precio_2011.iloc[0]['close']
    close_2023 = precio_2023.iloc[-1]['close']
    
    #CALCULAMOS EL TIPO DE CAMBIO DEL DOLAR INICIAL Y FINAL
    cambio_2011_data = cambio[cambio['anyo'] == 2011]
    cambio_2011 = cambio_2011_data['cambio'].iloc[0]#.MEAN()
    
    cambio_2023_data = cambio[cambio['anyo'] == 2023]
    cambio_2023 = cambio_2023_data['cambio'].iloc[0]#.mean()
    
    #CALCULAMOS EL PRECIO INICIAL Y FINAL DEL ETF EN LA MONEDA LOCAS
    close_local_2011 = close_2011 * cambio_2011
    close_local_2023 = close_2023 * cambio_2023

    #CALCULAMOS LA INFLACION ACUMULADA
    inflacion_acum = 1.0
    for year in range(2011, 2024):
        inf_anual = inflacion[inflacion['anyo'] == year]['inf_anual']
        if not inf_anual.empty:
            inflacion_acum *= (1 + inf_anual.iloc[0]/100)
   
   #CALCULAMOS EL PRECIO FINAL REAL EN MONEDA LOCAL DEL ETF
    close_2023_real = close_local_2023 / inflacion_acum
    
    #CALCULAMOS ENTONCES LA VARIACION QUE HUBO
    variacion_etf_pct = ((close_2023_real - close_local_2011) / close_local_2011) * 100
    
    #CALCULAMOS LOS WGI INICIAL Y FINAL DEL PAIS
    wgi_2011 = wgi[wgi['anyo'] == 2011].loc[:, 'valor'].mean()
    wgi_2023 = wgi[wgi['anyo'] == 2023].loc[:, 'valor'].mean()
    
    #CALCULAMOS LA VARIACION DEL WGI
    variacion_wgi_pct = ((wgi_2023 - wgi_2011) / abs(wgi_2011)) * 100

    #DEVOLVEMOS TODAS LAS METRICAS CALCULADAS
    return {
        'pais': pais,
        'wgi_2011': wgi_2011,
        'wgi_2023': wgi_2023,
        'variacion_wgi_pct': variacion_wgi_pct,
        'etf_2011': close_local_2011,
        'etf_2023': close_2023_real,
        'variacion_etf_pct': variacion_etf_pct,
        'close_usd_2011': close_2011,
        'close_usd_2023': close_2023,
        'fecha_2011': precio_2011.iloc[0]['date'].date(),
        'fecha_2023': precio_2023.iloc[-1]['date'].date()}

def calcular_correlaciones(df):
    #PARA PODER REALIZAR EL ANALISIS ESTADISTICO UTILIZAMOS LA LIBRE SCIPY PARA CALCULAR 
    #LOS COEFICIENTES DE CORRELACION DE PEARSON Y SPEARMAN

    print("CORRELACIONES 2011-2023")
    print("=" * 50)
    
    X = df['variacion_wgi_pct'].values
    y = df['variacion_etf_pct'].values
    
    r_pearson, p_pearson = pearsonr(X, y)
    r_spearman, p_spearman = spearmanr(X, y)
    
    print(f"Pearson:  r = {r_pearson:.4f}, p = {p_pearson:.4f}")
    print(f"Spearman: ρ = {r_spearman:.4f}, p = {p_spearman:.4f}")
    
    if p_pearson < 0.05:
        print("Correlacion Pearson significativa (p < 0.05)")
    else:
        print("Correlacion Pearson no significativa")
    
    if p_spearman < 0.05:
        print("Correlacion Spearman significativa (p < 0.05)")
    else:
        print("Correlacion Spearman no significativa")
    
    print()
    
def calcular_regresion(df):    
    #USAMOS EL PAQUETE SKLEARN PARA PODER CALCULAR LA REGRESION LINEAL DE LOS DATOS (Y LA R CUADRADA)
    X = df['variacion_wgi_pct'].values.reshape(-1, 1)
    y = df['variacion_etf_pct'].values
    
    reg = LinearRegression()
    reg.fit(X, y)
    
    r2 = reg.score(X, y)
    
    return reg, r2

def crear_scatter_plot(df, reg, r2):
    #DIBUJAMOS EL GRAFICO DE DISPERSION CON LA RESPECTIVA RECTA ED REGREFSION
    plt.figure(figsize=(10, 8))
    
    colores = {
        'spain':   '#D62728', 'colombia': '#FF7F0E',
        'brazil': '#2CA02C', 'italy': '#4682B4', 'germany': '#000000',
        'japan': '#E377C2', 'china': '#8C564B', 'usa': '#1E90FF', 'mexico': '#7F7F7F'
    }
    
    for col, row in df.iterrows():
        color = colores.get(row['pais'], '#333333')
        plt.scatter(row['variacion_wgi_pct'], row['variacion_etf_pct'], 
                   color=color, s=100, alpha=0.8, edgecolors='black', linewidth=1)
        plt.text(row['variacion_wgi_pct'], row['variacion_etf_pct'], 
                row['pais'].upper(), fontsize=9, ha='center', va='bottom')
    
    X_min = df['variacion_wgi_pct'].min() * 1.1
    X_max = df['variacion_wgi_pct'].max() * 1.1
    X_line = np.array([X_min, X_max])
    y_line = reg.intercept_ + reg.coef_[0] * X_line
    
    plt.plot(X_line, y_line, 'r--', linewidth=2, 
             label=f'R²={r2:.3f}')
    
    plt.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.7)
    plt.axvline(x=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.7)
    
    plt.xlabel('Variación WGI 2011→2023 (%)')
    plt.ylabel('Variación ETF Real 2011→2023 (%)')
    plt.title('Relación entre variación en WGI y rendimiento de ETF (2011-2023)')
    
    plt.axis('equal')
    
    plt.legend(loc='best')
    
    plt.tight_layout()
    plt.show()

#LLAMAMOS A LAS FUNCIONES
resultados = []

for pais in PAISES:
    res = calcular_variacion_2011_2023(pais)
    resultados.append(res)
    
df = pd.DataFrame(resultados)

calcular_correlaciones(df)

reg, r2 = calcular_regresion(df)

crear_scatter_plot(df, reg, r2)
