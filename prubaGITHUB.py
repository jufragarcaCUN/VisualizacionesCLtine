def cargar_y_mostrar_promedios(df):
    if df is not None and not df.empty:
        st.markdown("## 📊 Promedio por Columna Numérica")

        st.write("Columnas del DataFrame:", df.columns.tolist())

        columnas_numericas = df.select_dtypes(include='number').columns.tolist()
        num_columns = len(columnas_numericas)
        items_per_col = (num_columns + 3) // 4  # Divide en 4 columnas

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Aquí simplemente llamamos la función que imprime sus propios resultados
            promedio_general_calculado = calcular_promedio_total_numerico(df)
            st.metric(label="Promedio General Numérico", value=f"{promedio_general_calculado * 100:.2f}%")

        with col2:
            for col_name in columnas_numericas[items_per_col:items_per_col*2]:
                promedio = df[col_name].mean()
                st.metric(label=col_name, value=f"{promedio:.2f}")

        with col3:
            for col_name in columnas_numericas[items_per_col*2:items_per_col*3]:
                promedio = df[col_name].mean()
                st.metric(label=col_name, value=f"{promedio * 100:.2f}%")

        with col4:
            for col_name in columnas_numericas[items_per_col*3:]:
                promedio = df[col_name].mean()
                st.metric(label=col_name, value=f"{promedio * 100:.2f}%")
    else:
        st.warning("⚠️ El DataFrame está vacío o no ha sido cargado.")
