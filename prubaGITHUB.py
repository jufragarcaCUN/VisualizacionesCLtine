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
# Mantener solo las importaciones necesarias para el código visible o que se sabe que usas
from textblob import TextBlob

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ========================================
# === CONFIGURACIÓN DE STREAMLIT PAGE ===
# ========================================
st.set_page_config(layout="wide")


# ========================================
# === RUTAS A IMÁGENES ===================
# ========================================
carpetaImagenes = Path(r"C:\Users\juan_garnicac\OneDrive - Corporación Unificada Nacional de Educación Superior - CUN\Imágenes")
logoCun = carpetaImagenes / "CUN-1200X1200.png"
logoCltiene = carpetaImagenes / "clTiene2.jpeg"

# ========================================
# === RUTAS A ARCHIVOS DE DATOS =========
# ========================================
carpeta_principal = Path(r"C:\Users\juan_garnicac\OneDrive - Corporación Unificada Nacional de Educación Superior - CUN\Documentos\cltiene\audiosCltiene\cltieneAudios")
directorio_principal = carpeta_principal / "TranscribirAudios"

# Archivos específicos usando las rutas base definidas
ruta_archivo_reporte_puntaje = directorio_principal / "reporte_llamadas_asesores.xlsx"
ruta_archivo_sentimientos = directorio_principal / "sentimientos_textblob.xlsx"
# Nombre del archivo merge para el acordeon
nombre_archivo_reporte_acordeon = "acordon1.xlsx"
# Variable que guarda la ruta completa al archivo merge
puntejeAcordeoneros = directorio_principal / nombre_archivo_reporte_acordeon


# ========================================
# === CARGA DE DATAFRAMES ===============
# ========================================
# --- CARGA DEL DATAFRAME DE PUNTAJE DE ASESORES ---
try:
    df_puntajeAsesores = pd.read_excel(ruta_archivo_reporte_puntaje)
    print(f"✅ DataFrame df_puntajeAsesores cargado exitosamente desde: {ruta_archivo_reporte_puntaje}")
except FileNotFoundError:
    print(f"❌ ERROR: Archivo de Puntajes NO encontrado en: {ruta_archivo_reporte_puntaje}")
    st.error(f"❌ No se encontró el archivo de Puntajes: {ruta_archivo_reporte_puntaje}")
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
    print(f"❌ ERROR: Archivo de Sentimientos NO encontrado en: {ruta_archivo_sentimientos}")
    st.error(f"❌ No se encontró el archivo de Sentimientos: {ruta_archivo_sentimientos}")
    df_POlaVssub = pd.DataFrame()
except Exception as e:
    print(f"❌ ERROR: Falló al cargar df_POlaVssub desde '{ruta_archivo_sentimientos}': {e}")
    st.error(f"❌ Error al cargar sentimientos desde '{ruta_archivo_sentimientos}': {e}")
    df_POlaVssub = pd.DataFrame()

# --- CARGA DEL DATAFRAME PARA ACORDEONES ---
# Este es el DataFrame que se usa para la funcion mostrar_acordeones
# Asegurate de que el archivo 'acordon1.xlsx' haya sido creado (por el proceso de merge) antes de ejecutar este script Streamlit.
try:
    # Se carga el archivo merge 'acordon1.xlsx' usando la variable correcta
    df_acordeon = pd.read_excel(puntejeAcordeoneros) # Corregido: usar puntejeAcordeoneros
    print(f"✅ DataFrame df_acordeon cargado exitosamente desde: {puntejeAcordeoneros}")
except FileNotFoundError:
    print(f"❌ ERROR: Archivo de Acordeon NO encontrado en: {puntejeAcordeoneros}") # Corregido: usar puntejeAcordeoneros
    st.error(f"❌ No se encontró el archivo de Acordeon: {puntejeAcordeoneros}. Asegúrate de que el merge se haya ejecutado y guardado correctamente.") # Corregido: usar puntejeAcordeoneros
    df_acordeon = pd.DataFrame()
except Exception as e:
    print(f"❌ ERROR: Falló al cargar df_acordeon desde '{puntejeAcordeoneros}': {e}") # Corregido: usar puntejeAcordeoneros
    st.error(f"❌ Error al cargar acordeon desde '{puntejeAcordeoneros}': {e}") # Corregido: usar puntejeAcordeoneros
    df_acordeon = pd.DataFrame()


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

    with col2:
        img2_base64 = get_image_base64(logoCltiene)
        if img2_base64:
            st.markdown(f'<img src="data:image/png;base64,{img2_base64}" style="{img_style}"/>', unsafe_allow_html=True)


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
# La función ahora espera que el DataFrame contenga las columnas necesarias
# para mostrar el detalle (incluyendo las pares _%cumplimiento y _cumple, si se usa esa logica)
def mostrar_acordeones(df):
    import streamlit as st
    import pandas as pd

    # Verifica si el DataFrame es válido y si tiene la columna 'asesor'
    if df is None or df.empty:
        st.warning("⚠️ El DataFrame para los acordeones está vacío o no fue cargado correctamente.")
        return

    if 'asesor' not in df.columns:
        st.error("❌ El DataFrame para los acordeones no contiene la columna esencial: 'asesor'.")
        st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
        return

    st.markdown("<h3 style='text-align: center;'>🔍 Detalle Completo por Asesor</h3>", unsafe_allow_html=True)

    # Iterar sobre cada asesor
    for index, fila in df.iterrows():
        nombre_asesor = fila.get('asesor', f"Asesor Desconocido {index}")

        with st.expander(f"🧑 Detalle de: **{nombre_asesor}**"):
            columnas_a_mostrar = [col for col in df.columns if col != 'asesor']

            if not columnas_a_mostrar:
                st.info(f"ℹ️ No hay columnas para mostrar en el detalle de {nombre_asesor}.")
                continue

            for col_name in columnas_a_mostrar:
                value = fila[col_name]

                # Formatear valor para mostrar
                if pd.isna(value):
                    display_value = "N/A"
                elif isinstance(value, (int, float)):
                    try:
                        # Mostrar como flotante con un decimal
                        display_value = f"{value:.1f}"

                        # Ajustes según nombre de columna
                        if '%' in col_name or '_porcentaje' in col_name.lower():
                            display_value += "%"
                        elif 'puntaje' in col_name.lower():
                            display_value += ""  # sin % si es puntaje simple
                        elif value == int(value):
                            display_value = str(int(value))  # sin decimal si es entero exacto

                    except ValueError:
                        display_value = str(value)
                else:
                    display_value = str(value)

                # Asignar emoji según nombre de la columna (opcional)
                if 'saludo' in col_name.lower():
                    emoji = "👋"
                elif 'presentacion' in col_name.lower():
                    emoji = "🏢"
                elif 'politica' in col_name.lower():
                    emoji = "🔊"
                elif 'valor' in col_name.lower():
                    emoji = "💡"
                elif 'costos' in col_name.lower():
                    emoji = "💰"
                elif 'cierre' in col_name.lower():
                    emoji = "✅"
                elif 'normativo' in col_name.lower():
                    emoji = "📜"
                elif 'puntaje' in col_name.lower():
                    emoji = "⭐"
                elif 'sentimiento' in col_name.lower():
                    emoji = "😊"
                else:
                    emoji = "🔹"

                # Mostrar
                st.markdown(f"{emoji} **{col_name.replace('_', ' ').capitalize()}:** {display_value}")

# ========================================
# === FUNCIÓN PRINCIPAL STREAMLIT =======
# ========================================
def main():
  

    insetCodigo()

    # Llamada a las funciones de graficas y acordeones
    graficar_puntaje_total(df_puntajeAsesores)
    graficar_asesores_metricas_heatmap(df_puntajeAsesores)
    graficar_polaridad_subjetividad_gauges(df_POlaVssub)
    graficar_polaridad_por_asesor_barras_horizontales(df_POlaVssub)

    # --- Llamada a la funcion de acordeones ---
    # Debes pasar el DataFrame que contiene los datos para los acordeones (el merge)
    mostrar_acordeones(df_acordeon) # Corregido: pasar df_acordeon

# ========================================
# === EJECUCIÓN DEL PROGRAMA ============
# ========================================
if __name__ == '__main__':
    main()