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

st.set_page_config(layout="wide")

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

carpeta_base = Path(".")
logoCun = carpeta_base / "CUN-1200X1200.png"
logoCltiene = carpeta_base / "clTiene2.jpeg"

ruta_archivo_reporte_puntaje = carpeta_base / "reporte_llamadas_asesores.xlsx"
ruta_archivo_sentimientos = carpeta_base / "sentimientos_textblob.xlsx"
nombre_archivo_resultado_llamada_directo = "resultados_llamadas_directo.xlsx"
puntejeAcordeoneros = carpeta_base / nombre_archivo_resultado_llamada_directo
resumen_llamadita = carpeta_base / "resumen_llamadas.xlsx"
###############################################################################################
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
#################################################################
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
        height=1000,
        xaxis_tickangle=-45, plot_bgcolor="white",
        font=dict(family="Arial", size=12),
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True, key="puntaje_total_chart")

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
        colorbar=dict(title=dict(text="Valor (%)", font=dict(size=24)), tickfont=dict(size=24)),
        hovertemplate='Asesor: %{y}<br>Métrica: %{x}<br>Valor: %{z:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        title="Heatmap: Asesor vs. Métricas con Porcentaje (%)",
        xaxis_title="Métrica (%)", yaxis_title="Asesor",
        font=dict(family="Arial", size=12),
        height=700,
        title_x=0.5, plot_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True, key="heatmap_metrics_chart")

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
        if pd.isna(polaridad_total):
            polaridad_total = 0
    else:
        polaridad_total = 0

    if has_subjectivity:
        df['asesor'] = df['asesor'].apply(corregir_nombre)
        df['subjectivity'] = pd.to_numeric(df['subjectivity'], errors='coerce')
        subjetividad_total = df['subjectivity'].mean()
        if pd.isna(subjetividad_total):
            subjetividad_total = 0.5
    else:
        subjetividad_total = 0.5

    col1, col2 = st.columns(2)

    if has_polarity:
        with col1:
            fig_polaridad = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=polaridad_total,
                delta={
                    'reference': 0,
                    'increasing': {'color': 'green', 'symbol': '▲'},
                    'decreasing': {'color': 'red', 'symbol': '▼'},
                    'position': "bottom",
                    'font': {'size': 28}
                },
                gauge=dict(
                    axis=dict(range=[-1, 1]),
                    bar=dict(color='darkgreen'),
                    steps=[
                        {'range': [-1, -0.3], 'color': '#c7e9c0'},
                        {'range': [-0.3, 0.3], 'color': '#a1d99b'},
                        {'range': [0.3, 1], 'color': '#31a354'}
                    ],
                    threshold={'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0}
                ),
                title={'text': "Polaridad Promedio General", 'font': {'size': 18}},
                number={'font': {'size': 24}}
            ))
            fig_polaridad.update_layout(
                height=700,
                margin=dict(l=10, r=10, t=40, b=10),
                font=dict(family="Arial", size=12)
            )
            st.plotly_chart(fig_polaridad, use_container_width=True, key="gauge_polarity")
    else:
        with col1:
            st.info("Gauge de Polaridad no disponible.")

    if has_subjectivity:
        with col2:
            fig_subjetividad = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=subjetividad_total,
                delta={
                    'reference': 0.5,
                    'increasing': {'color': 'green', 'symbol': '▲'},
                    'decreasing': {'color': 'red', 'symbol': '▼'},
                    'position': "bottom",
                    'font': {'size': 28}
                },
                gauge=dict(
                    axis=dict(range=[0, 1]),
                    bar={'color': 'darkblue'},
                    steps=[
                        {'range': [0.0, 0.3], 'color': '#e5f5e0'},
                        {'range': [0.3, 0.7], 'color': '#a1d99b'},
                        {'range': [0.7, 1.0], 'color': '#31a354'}
                    ],
                    threshold={'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0.5}
                ),
                title={'text': "Subjetividad Promedio General", 'font': {'size': 18}},
                number={'font': {'size': 24}}
            ))
            fig_subjetividad.update_layout(
                height=700,
                margin=dict(l=10, r=10, t=40, b=10),
                font=dict(family="Arial", size=12)
            )
            st.plotly_chart(fig_subjetividad, use_container_width=True, key="gauge_subjectivity")
    else:
        with col2:
            st.info("Gauge de Subjetividad no disponible.")

def graficar_polaridad_por_asesor_barras_horizontales(df):
    def corregir_nombre_local(nombre):
        correcciones = {
            "danielalancheros": "Daniela Lancheros",
            "edwinmiranda": "Edwin Miranda",
            "luisareyes": "Luisa Reyes",
            "mayerlyacero": "Mayerly Acero",
            "nancymoreno": "Nancy Moreno",
            "nicolastovar": "Nicolas Tovar",
            "johan": "Johan",
            "noseentiendelenombredelasesor": "Desconocido",
            "noseescucha": "Desconocido",
            "notienenombre": "Desconocido"
        }
        if not nombre:
            return "Desconocido"
        nombre_str = str(nombre).strip().lower().replace(" ", "")
        return correcciones.get(nombre_str, str(nombre).title().strip())

    if df is None or df.empty:
        st.warning("⚠️ El DataFrame para la gráfica de Polaridad está vacío o no fue cargado correctamente.")
        return
    if 'asesor' not in df.columns or 'polarity' not in df.columns:
        st.error("❌ El DataFrame no contiene las columnas necesarias: 'asesor' y 'polarity'.")
        st.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
        return

    df['asesor'] = df['asesor'].astype(str).apply(corregir_nombre_local)
    df['polarity'] = pd.to_numeric(df['polarity'], errors='coerce')
    df_cleaned = df.dropna(subset=['asesor', 'polarity'])

    if df_cleaned.empty:
        st.warning("⚠️ No hay datos válidos para graficar.")
        return

    df_polaridad_avg = df_cleaned.groupby('asesor', as_index=False)['polarity'].mean()
    df_polaridad_avg = df_polaridad_avg.sort_values('polarity', ascending=True)

    fig = px.bar(
        df_polaridad_avg,
        x='asesor',
        y='polarity',
        title='Polaridad Promedio por Asesor',
        labels={'polarity': 'Polaridad Promedio', 'asesor': 'Asesor'},
        color_discrete_sequence=['green'],
        text='polarity'
    )

    fig.update_layout(
        yaxis_range=[-1, 1],
        xaxis_title="Asesor",
        yaxis_title="Polaridad Promedio",
        plot_bgcolor="White",
        height=700,
        font=dict(family="Arial", size=12),
        title_x=0.5
    )

    fig.update_traces(texttemplate='%{y:.3f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True, key="polarity_by_asesor_chart")

def mostrar_acordeones(df):
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

                columnas_conteo = [col for col in df.columns if col.endswith('_conteo')]

                for col in columnas_conteo:
                    categoria = col.replace('_conteo', '')
                    conteo = row.get(col, 'N/A')

                    cumple = '✅' if pd.notna(conteo) and conteo >= 1 else '❌'
                    st.write(f"  🔹 {categoria.replace('_', ' ').capitalize()}: {conteo} {cumple} (mínimo 1)")

                puntaje = row.get('puntaje_final_%', None)
                if pd.notna(puntaje):
                    resultado = 'Llamada efectiva' if puntaje >= 80 else 'No efectiva'
                    emoji = '✅' if puntaje >= 80 else '❌'
                    st.write(f"🎯 Resultado: {emoji} {resultado} — Puntaje: {puntaje:.1f}%")
                else:
                    st.write("🎯 Resultado: ? Resultado desconocido — Puntaje: N/A")

                if len(df_asesor) > 1 and index < len(df_asesor) - 1:
                    st.markdown("---")

def cargar_y_mostrar_columnas(df):
    if df is not None and not df.empty:
        st.markdown("## 📋 Columnas del DataFrame")

        all_columns = df.columns.tolist()
        num_columns = len(all_columns)
        items_per_col = (num_columns + 3) // 4  # Divide en 4 columnas visuales

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("### 📑 Col 1")
            for col_name in all_columns[0:items_per_col]:
                st.markdown(f"- `{col_name}`")

        with col2:
            st.markdown("### 📑 Col 2")
            for col_name in all_columns[items_per_col:items_per_col*2]:
                st.markdown(f"- `{col_name}`")

        with col3:
            st.markdown("### 📑 Col 3")
            for col_name in all_columns[items_per_col*2:items_per_col*3]:
                st.markdown(f"- `{col_name}`")

        with col4:
            st.markdown("### 📑 Col 4")
            for col_name in all_columns[items_per_col*3:]:
                st.markdown(f"- `{col_name}`")
    else:
        st.warning("⚠️ El DataFrame está vacío o no ha sido cargado.")

def main():
    insetCodigo()

    cargar_y_mostrar_columnas(df_POlaVssub)
    
    st.markdown("---")

    st.header("📈 Gráficos Resumen")

    graficar_puntaje_total(df_puntajeAsesores)

    st.markdown("---")

    graficar_asesores_metricas_heatmap(df_puntajeAsesores)

    st.markdown("---")

    graficar_polaridad_subjetividad_gauges(df_POlaVssub)

    st.markdown("---")

    graficar_polaridad_por_asesor_barras_horizontales(df_resumen)

    st.markdown("---")

    mostrar_acordeones(df_acordeon)
    cargar_y_mostrar_columnas(df_POlaVssub)


if __name__ == '__main__':
    main()
