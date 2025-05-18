# ========================================
# === IMPORTACIONES NECESARIAS ==========
# ========================================
import os
import re
import sys
import unicodedata
import base64
from pathlib import Path # Aunque ya no usamos Path para las rutas de archivos de datos/imagenes, se deja por si se usa en otra parte del script
from collections import defaultdict

import pandas as pd
# Mantener solo las importaciones necesarias
from textblob import TextBlob

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ========================================
# === CONFIGURACIÓN DE STREAMLIT PAGE ===
# ========================================
# ASEGURARSE QUE ESTA LINEA NO TIENE INDENTACION
st.set_page_config(layout="wide", title="Dashboard Cltiene") # Añadido titulo de nuevo


# ========================================
# === RUTAS A IMÁGENES ===================
# ========================================
# Archivos de imagen (deben estar en tu repositorio de GitHub)
# Asumiendo que estos archivos .png y .jpeg estan en la MISMA carpeta que tu script Python en GitHub:
logoCun = "CUN-1200X1200.png"
logoCltiene = "clTiene2.jpeg"

# Si los pusiste en una subcarpeta dentro de tu repositorio, por ejemplo './images/':
# logoCun = "./images/CUN-1200X1200.png"
# logoCltiene = "./images/clTiene2.jpeg"


# ========================================
# === RUTAS A ARCHIVOS DE DATOS =========
# ========================================
# Archivos de datos (deben estar en tu repositorio de GitHub)
# Asumiendo que estos archivos .xlsx estan en la MISMA carpeta que tu script Python en GitHub:
ruta_archivo_reporte_puntaje = "reporte_llamadas_asesores.xlsx"
ruta_archivo_sentimientos = "sentimientos_textblob.xlsx"
# Nombre del archivo merge para el acordeon
nombre_archivo_reporte_acordeon = "acordon1.xlsx"
# Variable que guarda la ruta del archivo merge (ahora es relativa)
puntejeAcordeoneros = nombre_archivo_reporte_acordeon

# Si los pusiste en una subcarpeta dentro de tu repositorio, por ejemplo './data/':
# ruta_archivo_reporte_puntaje = "./data/reporte_llamadas_asesores.xlsx"
# ruta_archivo_sentimientos = "./data/sentimientos_textblob.xlsx"
# puntejeAcordeoneros = "./data/acordon1.xlsx"


# ========================================
# === CARGA DE DATAFRAMES ===============
# ========================================
# --- CARGA DEL DATAFRAME DE PUNTAJE DE ASESORES ---
try:
    df_puntajeAsesores = pd.read_excel(ruta_archivo_reporte_puntaje)
    print(f"✅ DataFrame df_puntajeAsesores cargado exitosamente desde: {ruta_archivo_reporte_puntaje}")
except FileNotFoundError:
    print(f"❌ ERROR: Archivo de Puntajes NO encontrado en: {ruta_archivo_reporte_puntaje}. Asegúrate de que esté en el repositorio con el nombre correcto.")
    st.error(f"❌ No se encontró el archivo de Puntajes: {ruta_archivo_reporte_puntaje}. Asegúrate de que esté en el repositorio con el nombre correcto.")
    df_puntajeAsesores = pd.DataFrame()
except Exception as e:
    print(f"❌ ERROR: Falló al cargar df_puntajeAsesores desde '{ruta_archivo_reporte_puntaje}': {e}")
    st.error(f"❌ Error al cargar puntajes desde '{ruta_archivo_reporte_puntaje}': {e}")
    df_puntajeAsesores = pd.DataFrame()

# --- CARGA DEL DATAFRAME DE SENTIMIENTOS ---
try:
    df_POlaVssub = pd.read_excel(ruta_archivo_sentimientos)
    print(f"✅ DataFrame df_POlaVssub cargado exitosamente desde: {ruta_archivo_sentimientos}")
except FileNotFoundError:
    print(f"❌ ERROR: Archivo de Sentimientos NO encontrado en: {ruta_archivo_sentimientos}. Asegúrate de que esté en el repositorio con el nombre correcto.")
    st.error(f"❌ No se encontró el archivo de Sentimientos: {ruta_archivo_sentimientos}. Asegúrate de que esté en el repositorio con el nombre correcto.")
    df_POlaVssub = pd.DataFrame()
except Exception as e:
    print(f"❌ ERROR: Falló al cargar df_POlaVssub desde '{ruta_archivo_sentimientos}': {e}")
    st.error(f"❌ Error al cargar sentimientos desde '{ruta_archivo_sentimientos}': {e}")
    df_POlaVssub = pd.DataFrame()

# --- CARGA DEL DATAFRAME PARA ACORDEONES (Archivo Merge) ---
# Asegurate de que el archivo 'acordon1.xlsx' esté en el repositorio.
try:
    # Se carga el archivo merge 'acordon1.xlsx' usando la variable correcta
    df_acordeon = pd.read_excel(puntejeAcordeoneros)
    print(f"✅ DataFrame df_acordeon cargado exitosamente desde: {puntejeAcordeoneros}")
except FileNotFoundError:
    print(f"❌ ERROR: Archivo de Acordeon NO encontrado en: {puntejeAcordeoneros}. Asegúrate de que esté en el repositorio con el nombre correcto.")
    st.error(f"❌ No se encontró el archivo de Acordeon: {puntejeAcordeoneros}. Asegúrate de que esté en el repositorio con el nombre correcto.")
    df_acordeon = pd.DataFrame()
except Exception as e:
    print(f"❌ ERROR: Falló al cargar df_acordeon desde '{puntejeAcordeoneros}': {e}")
    st.error(f"❌ Error al cargar acordeon desde '{puntejeAcordeoneros}': {e}")
    df_acordeon = pd.DataFrame()


# ========================================
# === FUNCIONES DE SOPORTE ==============
# ========================================
# Nota: get_image_base64 ahora usa rutas relativas para los archivos de imagen
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        # Puedes añadir un print o log aqui si quieres ver errores de carga de imagen en la consola del servidor
        print(f"Error loading image {image_path}: {e}")
        return None

def insetCodigo():
    col1, col2 = st.columns(2)
    img_height = "150px"
    img_style = f"height: {img_height}; object-fit: contain; margin: auto; display: block;"

    # Usar las variables de ruta relativa definidas arriba
    img1_base64 = get_image_base64(logoCun)
    img2_base64 = get_image_base64(logoCltiene)

    with col1:
        if img1_base64:
            st.markdown(f'<img src="data:image/png;base64,{img1_base64}" style="{img_style}"/>', unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Imagen no encontrada: {logoCun}")

    with col2:
        if img2_base64:
            st.markdown(f'<img src="data:image/jpeg;base64,{img2_base64}" style="{img_style}"/>', unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Imagen no encontrada: {logoCltiene}")


# ========================================
# === GRÁFICAS ===========================
# ========================================
def graficar_puntaje_total(df):
    if df is None or df.empty or 'asesor' not in df.columns or 'puntaje_total' not in df.columns:
        st.warning("⚠️ Datos incompletos para la gráfica de puntaje total.")
        return

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
    fig.update_layout(height=600, xaxis_tickangle=-45, plot_bgcolor="white", font=dict(family="Arial", size=12), title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)


def graficar_asesores_metricas_heatmap(df):
    if df is None or df.empty or 'asesor' not in df.columns:
        st.warning("⚠️ Datos incompletos o faltan columnas necesarias ('asesor') para la gráfica heatmap.")
        return

    metric_cols = [col for col in df.columns if '%' in col]

    if not metric_cols:
        st.warning("⚠️ No se encontraron columnas con '%' en el DataFrame para graficar el heatmap.")
        return

    df_heatmap_data = df[['asesor'] + metric_cols].copy()
    df_heatmap_data = df_heatmap_data.set_index('asesor')

    df_heatmap_data = df_heatmap_data.apply(pd.to_numeric, errors='coerce').fillna(0)

    if df_heatmap_data.empty:
         st.warning("⚠️ Después de limpiar, el DataFrame para el heatmap está vacío.")
         return

    fig = go.Figure(data=go.Heatmap(
        z=df_heatmap_data.values,
        x=df_heatmap_data.columns,
        y=df_heatmap_data.index,
        colorscale='Greens',
        colorbar=dict(title="Valor (%)"),
        hovertemplate='Asesor: %{y}<br>Métrica: %{x}<br>Valor: %{z:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title="Heatmap: Asesor vs. Métricas con Porcentaje (%)",
        xaxis_title="Métrica (%)",
        yaxis_title="Asesor",
        font=dict(family="Arial", size=12),
        plot_bgcolor='white',
        height=max(400, len(df_heatmap_data.index) * 20 + 150),
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)


def graficar_polaridad_subjetividad_gauges(df):
    if df is None or df.empty:
        st.warning("⚠️ El DataFrame de Sentimientos está vacío o no fue cargado correctamente para los gauges.")
        return

    if 'polarity' not in df.columns or 'subjectivity' not in df.columns:
        st.error("❌ El DataFrame de Sentimientos no contiene las columnas necesarias: 'polarity' y 'subjectivity'.")
        return

    df['polarity'] = pd.to_numeric(df['polarity'], errors='coerce')
    df['subjectivity'] = pd.to_numeric(df['subjectivity'], errors='coerce')

    polaridad_total = df['polarity'].mean() if not df['polarity'].isnull().all() else 0
    subjetividad_total = df['subjectivity'].mean() if not df['subjectivity'].isnull().all() else 0.5

    if pd.isna(polaridad_total):
         st.warning("⚠️ No hay datos de Polaridad numéricos válidos para calcular el promedio.")
         polaridad_total = 0
    if pd.isna(subjetividad_total):
         st.warning("⚠️ No hay datos de Subjetividad numéricos válidos para calcular el promedio.")
         subjetividad_total = 0.5


    fig_polaridad = go.Figure(go.Indicator(
        mode="gauge+number",
        value=polaridad_total,
        gauge=dict(
            axis=dict(range=[-1, 1], tickwidth=1, tickcolor="darkblue"),
            bar=dict(color='darkgreen'),
            steps=[
                {'range': [-1, -0.3], 'color': 'lightcoral'},
                {'range': [-0.3, 0.3], 'color': 'khaki'},
                {'range': [0.3, 1], 'color': 'lightgreen'}
            ],
            threshold={'line': {'color': "red", 'width': 4}, 'thickness': 0.75,'value': 0 }
        ),
        title={'text': "Polaridad Promedio General", 'font': {'size': 18}},
        number={'font': {'size': 24}}
    ))

    fig_polaridad.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))

    fig_subjetividad = go.Figure(go.Indicator(
        mode="gauge+number",
        value=subjetividad_total,
         gauge=dict(
            axis={'range': [0, 1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            bar={'color': 'darkblue'},
            steps=[
                {'range': [0, 0.3], 'color': 'lightblue'},
                {'range': [0.3, 0.7], 'color': 'lightgray'},
                {'range': [0.7, 1], 'color': 'plum'}
            ],
             threshold={'line': {'color': "red", 'width': 4}, 'thickness': 0.75,'value': 0.5}
        ),
        title={'text': "Subjetividad Promedio General", 'font': {'size': 18}},
        number={'font': {'size': 24}}
    ))

    fig_subjetividad.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_polaridad, use_container_width=True)

    with col2:
        st.plotly_chart(fig_subjetividad, use_container_width=True)


def graficar_polaridad_por_asesor_barras_horizontales(df):
    if df is None or df.empty:
        st.warning("⚠️ El DataFrame para la gráfica de Polaridad (barras) está vacío o no fue cargado correctamente.")
        return

    if 'asesor' not in df.columns or 'polarity' not in df.columns:
        st.error("❌ El DataFrame no contiene las columnas necesarias para la gráfica de Polaridad (barras): 'asesor' y 'polarity'.")
        return

    df['polarity'] = pd.to_numeric(df['polarity'], errors='coerce')
    df_cleaned = df.dropna(subset=['asesor', 'polarity'])

    if df_cleaned.empty:
         st.warning("⚠️ No hay datos de Polaridad válidos por asesor para graficar barras.")
         return

    df_polaridad_avg = df_cleaned.groupby('asesor')['polarity'].mean().reset_index()

    fig = px.bar(
        df_polaridad_avg.sort_values('polarity', ascending=True),
        x='polarity',
        y='asesor',
        orientation='h',
        title='Polaridad Promedio por Asesor',
        labels={'polarity': 'Polaridad Promedio', 'asesor': 'Asesor'},
        color_discrete_sequence=['green']
    )

    fig.update_layout(
        xaxis_range=[-1, 1],
        yaxis_title="Asesor",
        xaxis_title="Polaridad Promedio",
        plot_bgcolor="white",
        height=max(400, len(df_polaridad_avg.index) * 30 + 100),
        title_x=0.5
    )

    st.plotly_chart(fig, use_container_width=True)


# ========================================
# === ANALISIS DETALLADO POR ASESOR (ACORDEONES) ===
# ========================================
# Esta función muestra TODAS las columnas del DataFrame para cada asesor dentro de un acordeón.
def mostrar_acordeones(df):
    # Verifica si el DataFrame es válido y si tiene la columna 'asesor'
    if df is None or df.empty:
        st.warning("⚠️ El DataFrame para los acordeones está vacío o no fue cargado correctamente.")
        return

    if 'asesor' not in df.columns:
         st.error("❌ El DataFrame para los acordeones no contiene la columna esencial: 'asesor'.")
         st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
         return

    st.markdown("<h3 style='text-align: center;'>🔍 Detalle Completo por Asesor</h3>", unsafe_allow_html=True)

    # Iterar sobre cada asesor (fila) del DataFrame
    for index, fila in df.iterrows():
        # Obtener el nombre del asesor
        nombre_asesor = fila.get('asesor', f"Asesor Desconocido {index}")

        # Crear acordeon para el asesor
        with st.expander(f"🧑 Detalle de: **{nombre_asesor}**"):
            # Obtener todas las columnas de la fila actual excepto 'asesor'
            columnas_a_mostrar = [col for col in df.columns if col != 'asesor']

            if not columnas_a_mostrar:
                 st.info(f"ℹ️ No hay columnas adicionales para mostrar en el detalle de {nombre_asesor}.")
                 continue

            # Mostrar cada columna y su valor
            for col_name in columnas_a_mostrar:
                 value = fila[col_name]

                 # Formatear valor
                 if pd.isna(value):
                      display_value = "N/A"
                 elif isinstance(value, (int, float)):
                      try:
                          # Formato numerico simple (1 decimal)
                          display_value = f"{value:.1f}"
                          # Ajustes heuristicos para % o puntaje vs conteo (sin decimales si es entero exacto)
                          if ('%' in col_name or '_porcentaje' in col_name.lower()) and not pd.isna(value):
                               display_value += "%"
                          elif value == int(value) and not pd.isna(value):
                                display_value = str(int(value))
                          # Si no es % o puntaje y es float, se queda con .1f por defecto


                      except ValueError: # En caso de error inesperado en formato numerico
                           display_value = str(value)
                 else: # Para strings u otros tipos
                     display_value = str(value)

                 # Asignar emoji según nombre de la columna (opcional, heuristica)
                 emoji = "🔹"
                 if 'saludo' in col_name.lower(): emoji = "👋"
                 elif 'presentacion' in col_name.lower(): emoji = "🏢"
                 elif 'politica' in col_name.lower(): emoji = "🔊"
                 elif 'valor' in col_name.lower(): emoji = "💡"
                 elif 'costos' in col_name.lower(): emoji = "💰"
                 elif 'cierre' in col_name.lower() or 'despedida' in col_name.lower(): emoji = "🚪"
                 elif 'normativo' in col_name.lower(): emoji = "📜"
                 elif 'puntaje' in col_name.lower(): emoji = "⭐"
                 elif 'sentimiento' in col_name.lower() or 'polarity' in col_name.lower() or 'subjectivity' in col_name.lower(): emoji = "😊"
                 elif '_cumple' in col_name.lower() or 'total_llamadas' in col_name.lower(): emoji = "📞"

                 # Mostrar
                 st.markdown(f"{emoji} **{col_name.replace('_', ' ').
