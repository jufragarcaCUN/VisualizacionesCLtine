# ========================================
# === IMPORTACIONES NECESARIAS ==========
# ========================================
import os
import re
import sys
import unicodedata
import base64
from pathlib import Path
from collections import defaultdict

import pandas as pd
from textblob import TextBlob

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from tabulate import tabulate

# ========================================
# === CONFIGURACIÓN DE STREAMLIT PAGE ===
# ========================================
st.set_page_config(layout="wide")

# ========================================
# === FUNCIONES DE SOPORTE ==============
# ========================================

def corregir_nombre(nombre):
    correcciones = {
        "DanielaLancheros": "Daniela Lancheros",
        "EdwinMiranda": "Edwin Miranda",
        "LuisaReyes": "Luisa Reyes",
        "MayerlyAcero": "Mayerly Acero",
        "NancyMoreno": "Nancy Moreno",
        "NicolasTovar": "Nicolas Tovar",
        "johan": "Johan",
        "NoseEntiendelenombredelasesor": "Desconocido",
        "NoSeEscucha": "Desconocido",
        "NotieneNombre": "Desconocido"
    }
    nombre_str = str(nombre).strip() if pd.notna(nombre) else ''
    return correcciones.get(nombre_str, nombre_str)

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def insetCodigo():
    col1, col2 = st.columns(2)
    img_height = "150px"
    img_style = f"height: {img_height}; object-fit: contain; margin: auto; display: block;"
    with col1:
        img1_base64 = get_image_base64(logoCun)
        if img1_base64:
            st.markdown(f'<img src="data:image/png;base64,{img1_base64}" style="{img_style}"/>', unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Logo CUN no encontrado en: {logoCun}")
    with col2:
        img2_base64 = get_image_base64(logoCltiene)
        if img2_base64:
            st.markdown(f'<img src="data:image/png;base64,{img2_base64}" style="{img_style}"/>', unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Logo Cltiene no encontrado en: {logoCltiene}")

# ========================================
# === RUTAS RELATIVAS ====================
# ========================================
carpeta_base = Path(".")
logoCun = carpeta_base / "CUN-1200X1200.png"
logoCltiene = carpeta_base / "clTiene2.jpeg"

ruta_archivo_reporte_puntaje = carpeta_base / "reporte_llamadas_asesores.xlsx"
ruta_archivo_sentimientos = carpeta_base / "sentimientos_textblob.xlsx"
nombre_archivo_reporte_acordeon = "acordon1.xlsx"
nombre_archivo_resultado_llamada_directo = "resultados_llamadas_directo.xlsx"
ruta_archivo_reporte_acordeon = carpeta_base / nombre_archivo_reporte_acordeon
puntejeAcordeoneros = carpeta_base / nombre_archivo_resultado_llamada_directo
resumen_llamadita = carpeta_base / "resumen_llamadas.xlsx"

# ========================================
# === CARGA DE DATAFRAMES ===============
# ========================================
try:
    df_puntajeAsesores = pd.read_excel(ruta_archivo_reporte_puntaje)
    if 'asesor' in df_puntajeAsesores.columns:
        df_puntajeAsesores['asesor'] = df_puntajeAsesores['asesor'].apply(corregir_nombre)
except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo de Puntajes: {ruta_archivo_reporte_puntaje}")
    df_puntajeAsesores = pd.DataFrame()
except Exception as e:
    st.error(f"❌ Error al cargar puntajes desde '{ruta_archivo_reporte_puntaje}': {e}")
    df_puntajeAsesores = pd.DataFrame()

try:
    df_POlaVssub = pd.read_excel(ruta_archivo_sentimientos)
    if 'asesor' in df_POlaVssub.columns:
        df_POlaVssub['asesor'] = df_POlaVssub['asesor'].apply(corregir_nombre)

    if 'sentimiento_promedio_polaridad' in df_POlaVssub.columns:
        df_POlaVssub.rename(columns={'sentimiento_promedio_polaridad': 'polarity'}, inplace=True)
        if 'subjectivity' not in df_POlaVssub.columns:
            df_POlaVssub['subjectivity'] = 0.5
    elif 'polarity' not in df_POlaVssub.columns:
        st.error(f"❌ El archivo '{ruta_archivo_sentimientos.name}' no tiene las columnas de polaridad esperadas.")
        df_POlaVssub = pd.DataFrame()
except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo de Sentimientos: {ruta_archivo_sentimientos}")
    df_POlaVssub = pd.DataFrame()
except Exception as e:
    st.error(f"❌ Error al cargar sentimientos desde '{ruta_archivo_sentimientos}': {e}")
    df_POlaVssub = pd.DataFrame()

try:
    df_acordeon = pd.read_excel(puntejeAcordeoneros)
    if 'asesor' in df_acordeon.columns:
        df_acordeon['asesor'] = df_acordeon['asesor'].apply(corregir_nombre)
except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo de Acordeon: {puntejeAcordeoneros}.")
    df_acordeon = pd.DataFrame()
except Exception as e:
    st.error(f"❌ Error al cargar acordeon desde '{puntejeAcordeoneros}': {e}")
    df_acordeon = pd.DataFrame()

try:
    df_resumen = pd.read_excel(resumen_llamadita)
    df_resumen['asesor'] = df_resumen['asesor'].apply(corregir_nombre)
except FileNotFoundError:
    st.error(f"⚠️ No se encontró el archivo resumen: {resumen_llamadita}")
    df_resumen = pd.DataFrame()
except Exception as e:
    st.error(f"⚠️ Ocurrió un error al leer el archivo resumen: {e}")
    df_resumen = pd.DataFrame()

try:
    resultados_llamadas_directo = pd.read_excel(ruta_archivo_reporte_puntaje)
    print(f"Archivo {ruta_archivo_reporte_puntaje.name} importado correctamente.")
    print(tabulate(resultados_llamadas_directo.head(), headers='keys', tablefmt='psql'))
except FileNotFoundError:
    print(f"No se encontró el archivo: {ruta_archivo_reporte_puntaje}")
    resultados_llamadas_directo = pd.DataFrame()
except Exception as e:
    print(f"Error al importar el archivo {ruta_archivo_reporte_puntaje.name}: {e}")
    resultados_llamadas_directo = pd.DataFrame()

try:
    acordeonYesid = pd.read_excel(ruta_archivo_reporte_acordeon)
    st.success(f"Archivo {nombre_archivo_reporte_acordeon} cargado correctamente.")
except FileNotFoundError:
    st.error(f"No se encontró el archivo: {nombre_archivo_reporte_acordeon}")
    acordeonYesid = pd.DataFrame()
except Exception as e:
    st.error(f"Error cargando {nombre_archivo_reporte_acordeon}: {e}")
    acordeonYesid = pd.DataFrame()



# ========================================
# === FUNCIONES DE SOPORTE ==============
# ========================================
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def insetCodigo():
    col1, col2 = st.columns(2)
    img_height = "150px"
    img_style = f"height: {img_height}; object-fit: contain; margin: auto; display: block;"
    with col1:
        img1_base64 = get_image_base64(logoCun)
        if img1_base64:
            st.markdown(f'<img src="data:image/png;base64,{img1_base64}" style="{img_style}"/>', unsafe_allow_html=True)
        else:
             st.warning(f"⚠️ Logo CUN no encontrado en: {logoCun}")
    with col2:
        img2_base64 = get_image_base64(logoCltiene)
        if img2_base64:
            st.markdown(f'<img src="data:image/png;base64,{img2_base64}" style="{img_style}"/>', unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Logo Cltiene no encontrado en: {logoCltiene}")

def corregir_nombre(nombre):
    correcciones = {
        "DanielaLancheros": "Daniela Lancheros",
        "EdwinMiranda": "Edwin Miranda",
        "LuisaReyes": "Luisa Reyes",
        "MayerlyAcero": "Mayerly Acero",
        "NancyMoreno": "Nancy Moreno",
        "NicolasTovar": "Nicolas Tovar",
        "johan": "Johan",
        "NoseEntiendelenombredelasesor": "Desconocido",
        "NoSeEscucha": "Desconocido",
        "NotieneNombre": "Desconocido"
    }
    nombre_str = str(nombre).strip() if pd.notna(nombre) else ''
    return correcciones.get(nombre_str, nombre_str)


# ========================================
# === GRÁFICAS ===========================
# ========================================
def graficar_puntaje_total(df):
    if df is None or df.empty or 'asesor' not in df.columns or 'puntaje_total' not in df.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de puntaje total.")
        return
    df['asesor'] = df['asesor'].apply(corregir_nombre)    
    df['puntaje_total'] = pd.to_numeric(df['puntaje_total'], errors='coerce')
    df_cleaned = df.dropna(subset=['asesor', 'puntaje_total'])
    if df_cleaned.empty:
        st.warning("⚠️ No hay datos válidos de asesor o puntaje total para graficar.")
        return
    fig = px.bar(
        df_cleaned.sort_values("puntaje_total", ascending=False),
        x="asesor",
        y="puntaje_total",
        text="puntaje_total",
        color="puntaje_total",
        color_continuous_scale="Greens",
        title="🎯 Puntaje Total Ponderado por Asesor",
        labels={"puntaje_total": "Puntaje Total Ponderado", "asesor": "Asesor"}
    )
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(
        height=700, # Misma altura para todas las gráficas
        xaxis_tickangle=-45, plot_bgcolor="white",
        font=dict(family="Arial", size=12), # Tamaño de fuente original del código proporcionado
        title_x=0.5
    )
    # --- Inicia Gráfico: Puntaje Total ---
    st.plotly_chart(fig, use_container_width=True)
    # --- Fin Gráfico: Puntaje Total ---


def graficar_asesores_metricas_heatmap(df):
    if df is None or df.empty or 'asesor' not in df.columns:
        st.warning("⚠️ Datos incompletos o faltan columnas necesarias ('asesor') para la gráfica heatmap.")
        return
    metric_cols = [col for col in df.columns if '%' in col]
    if not metric_cols:
        st.warning("⚠️ No se encontraron columnas con '%' en el DataFrame para graficar el heatmap.")
        st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
        return
    df['asesor'] = df['asesor'].apply(corregir_nombre)       
    df_heatmap_data = df[['asesor'] + metric_cols].copy()
    df_heatmap_data = df_heatmap_data.set_index('asesor')
    df_heatmap_data = df_heatmap_data.apply(pd.to_numeric, errors='coerce').fillna(0)
    if df_heatmap_data.empty:
        st.warning("⚠️ Después de limpiar, el DataFrame para el heatmap está vacío.")
        return
    fig = go.Figure(data=go.Heatmap(
        z=df_heatmap_data.values, x=df_heatmap_data.columns, y=df_heatmap_data.index,
        colorscale='Greens',
        colorbar=dict(title=dict(text="Valor (%)", font=dict(size=24)), tickfont=dict(size=24)), # Corregido sintaxis, mantiene tamaño original
        hovertemplate='Asesor: %{y}<br>Métrica: %{x}<br>Valor: %{z:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        title="Heatmap: Asesor vs. Métricas con Porcentaje (%)",
        xaxis_title="Métrica (%)", yaxis_title="Asesor",
        font=dict(family="Arial", size=12), # Tamaño de fuente original del código proporcionado
        height=700, # Misma altura para todas las gráficas
        title_x=0.5, plot_bgcolor='white'
    )
    # --- Inicia Gráfico: Heatmap Métricas ---
    st.plotly_chart(fig, use_container_width=True)
    # --- Fin Gráfico: Heatmap Métricas ---


def graficar_polaridad_subjetividad_gauges(df):
    if df is None or df.empty:
        st.warning("⚠️ El DataFrame de Sentimientos está vacío o no fue cargado correctamente para los gauges.")
        return
    if 'polarity' not in df.columns:
         st.error("❌ El DataFrame de Sentimientos no contiene la columna 'polarity' necesaria para el gauge de polaridad.")
         st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
         has_polarity = False
    else:
         has_polarity = True
    if 'subjectivity' not in df.columns:
        st.warning("⚠️ El DataFrame de Sentimientos no contiene la columna 'subjectivity'. El gauge de subjetividad no se mostrará.")
        st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
        has_subjectivity = False
    else:
         has_subjectivity = True
    if not has_polarity and not has_subjectivity:
         st.error("❌ No hay columnas válidas ('polarity', 'subjectivity') en el DataFrame de Sentimientos para generar ningún gauge.")
         return

    if has_polarity:
        df['asesor'] = df['asesor'].apply(corregir_nombre)   
        df['polarity'] = pd.to_numeric(df['polarity'], errors='coerce')
        polaridad_total = df['polarity'].mean()
        if pd.isna(polaridad_total): polaridad_total = 0
    else: polaridad_total = 0

    if has_subjectivity:
        df['asesor'] = df['asesor'].apply(corregir_nombre)   
        df['subjectivity'] = pd.to_numeric(df['subjectivity'], errors='coerce')
        subjetividad_total = df['subjectivity'].mean()
        if pd.isna(subjetividad_total): subjetividad_total = 0.5
    else: subjetividad_total = 0.5

    col1, col2 = st.columns(2)

    # --- Inicia Gráfico: Gauges Sentimiento General ---
    if has_polarity:
        with col1:
            df['asesor'] = df['asesor'].apply(corregir_nombre)   
            fig_polaridad = go.Figure(go.Indicator(
                mode="gauge+number", value=polaridad_total,
                gauge=dict(
                    axis=dict(range=[-1, 1]), # Configuración original de axis
                    bar=dict(color='darkgreen'), # Color original de la barra
                    steps=[
                        # PASOS Y COLORES ESPECIFICADOS POR TI AHORA para Polaridad
                        {'range': [-1, -0.3], 'color': '#c7e9c0'},
                        {'range': [-0.3, 0.3], 'color': '#a1d99b'},
                        {'range': [0.3, 1], 'color': '#31a354'}
                    ],
                    threshold={'line': {'color': "red", 'width': 4}, 'thickness': 0.75,'value': 0 }
                ),
                title={'text': "Polaridad Promedio General", 'font': {'size': 18}}, # Tamaño de fuente original
                number={'font': {'size': 24}} # Tamaño de fuente original
            ))
            fig_polaridad.update_layout(
                 height=700, # Misma altura para todas las gráficas
                 margin=dict(l=10, r=10, t=40, b=10),
                 font=dict(family="Arial", size=12) # Tamaño de fuente base original
            )
            st.plotly_chart(fig_polaridad, use_container_width=True)
    else:
         with col1: st.info("Gauge de Polaridad no disponible.")

    if has_subjectivity:
        with col2:
            fig_subjetividad = go.Figure(go.Indicator(
                mode="gauge+number", value=subjetividad_total,
                gauge=dict(
                    # --- CORRECCIÓN DE SINTAXIS AQUÍ (axis definition) ---
                    axis=dict(range=[0, 1]), # Corregido sintaxis, configuración original
                    # --- FIN CORRECCIÓN ---
                    bar={'color': 'darkblue'}, # Color original de la barra de subjetividad
                    steps=[
                         # Pasos y colores originales del gauge de subjetividad (del código que me diste antes de la confusión de colores)
                         {'range': [0.0, 0.3], 'color': '#e5f5e0'},
                         {'range': [0.3, 0.7], 'color': '#a1d99b'},
                         {'range': [0.7, 1.0], 'color': '#31a354'}
                    ],
                    threshold={'line': {'color': "red", 'width': 4}, 'thickness': 0.75,'value': 0.5}
                ),
                title={'text': "Subjetividad Promedio General", 'font': {'size': 18}}, # Tamaño de fuente original
                number={'font': {'size': 24}} # Tamaño de fuente original
            ))
            fig_subjetividad.update_layout(
                 height=700, # Misma altura para todas las gráficas
                 margin=dict(l=10, r=10, t=40, b=10),
                 font=dict(family="Arial", size=12) # Tamaño de fuente base original
            )
            st.plotly_chart(fig_subjetividad, use_container_width=True)
    else:
         with col2: st.info("Gauge de Subjetividad no disponible.")
    # --- Fin Gráfico: Gauges Sentimiento General ---


import streamlit as st
import pandas as pd
import plotly.express as px

def graficar_polaridad_por_asesor_barras_horizontales(df):
    if df is None or df.empty:
        st.warning("⚠️ El DataFrame para la gráfica de Polaridad está vacío o no fue cargado correctamente.")
        return
    if 'asesor' not in df.columns or 'polarity' not in df.columns:
        st.error("❌ El DataFrame no contiene las columnas necesarias: 'asesor' y 'polarity'.")
        st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
        return

    # Corregir nombres de asesores y convertir a numérico
    df['asesor'] = df['asesor'].apply(corregir_nombre)
    df['polarity'] = pd.to_numeric(df['polarity'], errors='coerce')
    df_cleaned = df.dropna(subset=['asesor', 'polarity'])

    if df_cleaned.empty:
        st.warning("⚠️ No hay datos válidos para graficar.")
        return

    # Agrupar por asesor y calcular promedio de polaridad
    df_polaridad_avg = df_cleaned.groupby('asesor', as_index=False)['polarity'].mean()
    df_polaridad_avg = df_polaridad_avg.sort_values('polarity', ascending=True)

    # Crear gráfico de barras verticales
    fig = px.bar(
        df_polaridad_avg,
        x='asesor',
        y='polarity',
        title='Polaridad Promedio por Asesor',
        labels={'polarity': 'Polaridad Promedio', 'asesor': 'Asesor'},
        color_discrete_sequence=['green']
    )

    # Ajustes de layout
    fig.update_layout(
        yaxis_range=[-1, 1],
        xaxis_title="Asesor",
        yaxis_title="Polaridad Promedio",
        plot_bgcolor="White",
        height=700,
        font=dict(family="Arial", size=12),
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)
# ========================================
# === ANALISIS DETALLADO POR ASESOR (ACORDEONES) ===
# ========================================
def mostrar_acordeones(df):
    # Validamos que el DataFrame no esté vacío ni sea None
    if df is None or df.empty:
        st.warning("⚠️ El DataFrame está vacío o no fue cargado correctamente.")
        return

    # Obtenemos la lista única de asesores presentes en la columna 'asesor'
    asesores = df['asesor'].unique()

    # Iteramos por cada asesor
    for asesor in asesores:
        # Filtramos las filas del DataFrame que pertenecen al asesor actual
        df_asesor = df[df['asesor'] == asesor]

        # OMITIMOS LA VISUALIZACIÓN CON EXPANDER PARA QUE NO SE MUESTRE
        # En vez de usar st.expander, simplemente no mostramos nada

        # Esta parte del código queda funcional pero oculta
        for i, fila in df_asesor.iterrows():
            #st.markdown("---")  # Línea divisoria entre llamadas

            # Iteramos por cada columna del DataFrame (excepto 'asesor')
            for columna in df.columns:
                if columna == 'asesor':
                    continue  # Saltamos la columna 'asesor'

                # Obtenemos el valor de esta columna para la fila actual
                valor = fila[columna]
                try:
                    # Intentamos convertir el valor a entero
                    valor_int = int(valor)

                    # Verificamos si cumple con el mínimo (al menos 1)
                    estado = "✅" if valor_int >= 1 else "❌"

                    # Mostramos la categoría, el valor y el estado
                    # Esta línea es la que normalmente mostraría contenido
                    # st.markdown(f"🔹 {columna}: {valor_int} {estado} (mínimo 1)")
                except:
                    # Si el valor no es numérico, lo mostramos tal cual
                    # st.markdown(f"🔹 {columna}: {valor}")
                    pass


#000000000000000000000000000000000000000
#0000000 acordeon Yesid
##################################

# ========================================
# === ANALISIS DETALLADO POR ASESOR (ACORDEONES) ===
# ========================================
# Asegúrate de que la función corregir_nombre esté definida antes en el script
# Asegúrate de que las importaciones principales (pandas, streamlit) estén al inicio del script
# Si prefieres importar dentro de la función, mantén las líneas de importación aquí

import streamlit as st
import pandas as pd

def mostrar_acordeones_simple(df):
    if df is None or df.empty:
        st.warning("⚠️ El DataFrame está vacío o no fue cargado correctamente.")
        return
    if 'asesor' not in df.columns:
        st.error("❌ El DataFrame no contiene la columna 'asesor'.")
        return

    st.markdown("### 🔍 Detalle Completo por Asesor")

    df['asesor'] = df['asesor'].astype(str)
    unique_asesores = df['asesor'].dropna().unique()

    for nombre_asesor in unique_asesores:
        df_asesor = df[df['asesor'] == nombre_asesor]

        with st.expander(f"🧑 Detalle de: **{nombre_asesor}**"):
            for index, row in df_asesor.iterrows():
                filename = row.get('archivo', 'Archivo desconocido')
                st.write(f"Analizando: **{filename}**")

                # Detectar automáticamente las columnas *_conteo
                columnas_conteo = [col for col in df.columns if col.endswith('_conteo')]

                for col in columnas_conteo:
                    categoria = col.replace('_conteo', '')
                    conteo = row.get(col, 'N/A')

                    # Mostrar ✅ o ❌ basado en conteo
                    cumple = '✅' if pd.notna(conteo) and conteo >= 1 else '❌'
                    st.write(f"  🔹 {categoria.replace('_', ' ').capitalize()}: {conteo} {cumple} (mínimo 1)")

                # Mostrar puntaje y resultado final
                puntaje = row.get('puntaje_final_%', None)
                if pd.notna(puntaje):
                    resultado = 'Llamada efectiva' if puntaje >= 80 else 'No efectiva'
                    emoji = '✅' if puntaje >= 80 else '❌'
                    st.write(f"🎯 Resultado: {emoji} {resultado} — Puntaje: {puntaje:.1f}%")
                else:
                    st.write("🎯 Resultado: ? Resultado desconocido — Puntaje: N/A")

                if len(df_asesor) > 1 and index < len(df_asesor) - 1:
                    st.markdown("---")
                    #############nuevo acordeon 

# ========================================
# === FUNCIÓN PRINCIPAL STREAMLIT =======
# ========================================
def main():

    # --- Inicia Titulo de la Aplicación (Letra Más Grande) ---
    st.title("📊 Reporte de Llamadas y Sentimiento por Asesor")
    # --- Fin Titulo de la Aplicación ---

    insetCodigo()

    # --- Separa un grafico ---
    st.markdown("---")
    # --- Fin separación ---

    # --- Inicia sección Gráficos Resumen (Letra Más Grande) ---
    st.header("📈 Gráficos Resumen")
    # --- Fin sección Gráficos Resumen ---

    # --- Inicia Gráfico: Puntaje Total ---
    graficar_puntaje_total(df_puntajeAsesores)
    # --- Fin Gráfico: Puntaje Total ---

    # --- Separa un grafico ---
    st.markdown("---")
    # --- Fin separación ---

    # --- Inicia Gráfico: Heatmap Métricas ---
    graficar_asesores_metricas_heatmap(df_puntajeAsesores)
    # --- Fin Gráfico: Heatmap Métricas ---

    # --- Separa un grafico ---
    st.markdown("---")
    # --- Fin separación ---

    # --- Inicia Gráfico: Gauges Sentimiento General ---
    graficar_polaridad_subjetividad_gauges(df_POlaVssub)
    # --- Fin Gráfico: Gauges Sentimiento General ---

    # --- Separa un grafico ---
    st.markdown("---")
    # --- Fin separación ---
    graficar_polaridad_por_asesor_barras_horizontales(df_resumen)



    # --- Separa un grafico ---
    st.markdown("---")
    # --- Fin separación ---

    # --- Inicia sección Detalle por Asesor ---
    mostrar_acordeones(df_acordeon)
    # --- Fin sección Detalle por Asesor ---
    mostrar_acordeones_simple(df_acordeon)


# ========================================
# === EJECUCIÓN DEL PROGRAMA ============
# ========================================
if __name__ == '__main__':
    main()
