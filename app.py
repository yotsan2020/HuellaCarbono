import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px


# --- Configuración inicial ---
st.set_page_config(
    page_title="Huella de Carbono",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- Logo en la barra lateral ---
st.sidebar.image("huellac.png", use_column_width=True)
st.sidebar.title("Menú de Navegación")


# --- Conexión a la base de datos ---
conn = sqlite3.connect("huellacarbono.db")
cursor = conn.cursor()


# --- Función para cargar datos ---
def cargar_datos(query):
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# --- Opciones de navegación ---
opcion = st.sidebar.radio(
    "Selecciona una vista:",
    ("Cocina y eficiencia", "Horas de actividad",  "Promedio de transporte","Huella por transporte")
)


if opcion == "Cocina y eficiencia":
    st.header("Cocina y Eficiencia Energética")
    query = "SELECT * FROM cocina_eficiencia_huella"
    datos = cargar_datos(query)

    # --- Caja de búsqueda ---
    st.subheader("Buscar por ID de Persona")
    id_buscar = st.text_input("Ingresa el IDPersona:")
    if id_buscar:
        datos = datos[datos["IDPersona"] == int(id_buscar)]

    # --- Dos columnas ---
    col1, col2 = st.columns(2)

    # Tabla en la primera columna
    with col1:
        st.subheader("Tabla Elementos Cocina")
        st.dataframe(datos)
        
    # --- Gráfico en la segunda columna ---
    with col2:
        st.subheader("Conteo de Registros por Elemento de Cocina")
        try:
            # Cargar los datos originales sin filtro
            datos_grafico = cargar_datos(query)
            
            # Contar cuántas veces aparece cada ElementoCocina
            grafico_data = (
                datos_grafico.groupby("ElementoCocina", as_index=False)
                .size()  # Cuenta los registros por cada ElementoCocina
                .rename(columns={"size": "ConteoRegistros"})
            )

            # Crear el gráfico con Plotly
            fig = px.bar(
                grafico_data,
                x="ElementoCocina",
                y="ConteoRegistros",
                color="ElementoCocina",
                title="Conteo de Registros por Elemento de Cocina",
                labels={"ElementoCocina": "Elemento de Cocina", "ConteoRegistros": "Número de Registros"},
                color_discrete_sequence=["#c9eab8"]  # Todos los colores en el gráfico serán de este color
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al procesar el gráfico: {e}")

# --- Visualización de la tabla y gráfico en la segunda columna ---
if opcion == "Horas de actividad":
    st.header("Horas de Actividad y Uso de Tecnología")
    query = "SELECT * FROM horas_actividad_otro"
    datos = cargar_datos(query)
    
    # Filtro para seleccionar "Hombres" o "Mujeres"
    genero = st.selectbox("Selecciona el género:", ["Todos", "male", "female"])
    
    # Filtrar datos por género seleccionado
    if genero != "Todos":
        datos = datos[datos["Sex"] == genero]
    
    # Crear las dos columnas para la tabla y el gráfico
    col1, col2 = st.columns([1, 1])  # Dos columnas de igual tamaño
    
    # Mostrar la tabla en la primera columna
    with col1:
        st.dataframe(datos)

    # --- Gráfico en la segunda columna (independiente del filtro) ---
    with col2:
        st.subheader("Gráfico de Horas de Internet y TV por Género")
        
        try:
            # Datos originales sin filtro para el gráfico
            datos_grafico = cargar_datos(query)
            
            # Agrupar por género y calcular el promedio de horas de TV e Internet
            grafico_data = (
                datos_grafico.groupby("Sex", as_index=False)
                .agg({
                    "DailyHourTVPC": "mean",
                    "DailyHourInternrt": "mean"
                })
            )
            
            # Reestructurar los datos para tener las horas de TV y de Internet en columnas separadas
            grafico_data_melted = grafico_data.melt(id_vars=["Sex"], 
                                                    value_vars=["DailyHourTVPC", "DailyHourInternrt"], 
                                                    var_name="Actividad", 
                                                    value_name="Horas Promedio")
            
            # Crear el gráfico de barras con colores específicos por género y actividad
            fig = px.bar(
                grafico_data_melted,
                x="Sex",
                y="Horas Promedio",
                color="Actividad",
                title="Promedio de Horas de TV e Internet por Género",
                labels={"Sex": "Género", "Horas Promedio": "Horas Promedio", "Actividad": "Actividad"},
                color_discrete_map={
                    "DailyHourTVPC": "#97c182",  # Azul fuerte para TV
                    "DailyHourInternrt": "#c9eab8",  # Azul claro para Internet
                    "female": "#ff7f0e",  # Naranja fuerte para mujer
                    "male": "#ffbb78",  # Naranja claro para mujer
                },
                barmode="group",  # Para barras agrupadas
            )

            # Mostrar el gráfico en la aplicación
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al procesar el gráfico: {e}")





# --- Huella de Carbono por Transporte ---
elif opcion == "Huella por transporte":
    st.header("Huella de Carbono por Transporte")
    query = "SELECT * FROM huella_carbono_por_transporte"
    datos = cargar_datos(query)

    # Asegurarnos de que las columnas tienen el nombre correcto
    datos.rename(columns={
        'TipoDeTransporte': 'TipoDeTransporte', 
        'PromedioHuellaCarbono': 'PromedioHuella'
    }, inplace=True)

    # Convertir la columna 'PromedioHuella' a tipo numérico para evitar errores
    datos['PromedioHuella'] = pd.to_numeric(datos['PromedioHuella'], errors='coerce')

    # Crear las dos columnas para la tabla y el gráfico
    col1, col2 = st.columns([1, 1])  # Dos columnas de igual tamaño

    # Mostrar la tabla en la primera columna
    with col1:
        st.dataframe(datos)

    # Crear el gráfico de barras en la segunda columna
    with col2:
        st.subheader("Gráfico de Huella de Carbono por Transporte")

        try:
            # Crear el gráfico de barras
            fig = px.bar(
                datos,
                x="TipoDeTransporte",  # Columna del eje x
                y="PromedioHuella",    # Columna del eje y
                title="Huella de Carbono por Transporte",
                labels={"TipoDeTransporte": "Tipo de Transporte", "PromedioHuella": "Promedio de Huella de Carbono"},
                color="TipoDeTransporte",  # Usar color basado en el tipo de transporte
                color_discrete_sequence=["#c9eab8"]  # Paleta de colores personalizada
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al procesar el gráfico: {e}")




# --- Promedio de Huella de Carbono por Frecuencia de Viajes ---
elif opcion == "Promedio de transporte":
    st.header("Promedio de Huella de Carbono por Frecuencia de Viajes")
    query = "SELECT * FROM promedio_transporte"
    datos = cargar_datos(query)

    # Renombrar columnas para que coincidan con el código
    datos.rename(columns={
        'FrecuencyTraveling': 'TipoDeTransporte', 
        'PromedioHuellaCarbono': 'PromedioHuella'
    }, inplace=True)

    # Convertir la columna 'PromedioHuella' a tipo numérico si no lo es
    datos['PromedioHuella'] = pd.to_numeric(datos['PromedioHuella'], errors='coerce')

    # Crear las dos columnas para la tabla y el gráfico
    col1, col2 = st.columns([1, 1])  # Dos columnas de igual tamaño

    # Mostrar la tabla en la primera columna
    with col1:
        st.dataframe(datos)

    # Crear un gráfico de barras apiladas en la segunda columna
    with col2:
        import plotly.express as px

        # Crear el gráfico de barras
        fig = px.bar(
            datos,
            x='TipoDeTransporte',  # Columna del eje x
            y='PromedioHuella',    # Columna del eje y
            color='TipoDeTransporte',  # Color basado en el tipo de transporte
            title="Huella de Carbono por Tipo de Transporte",
            labels={'TipoDeTransporte': 'Tipo de Transporte', 'PromedioHuella': 'Promedio de Huella de Carbono'},
            color_discrete_sequence=["#c9eab8"]
        )

        # Mostrar el gráfico
        st.plotly_chart(fig)




# --- Pie de página ---
st.sidebar.markdown("### 🌍 Reduce tu huella de carbono")