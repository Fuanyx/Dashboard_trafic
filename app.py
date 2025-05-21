import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import plotly.express as px
import pandas as pd
import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
import psycopg2
import pandas as pd
import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit_authenticator as stauth

# Parámetros de conexión (ajusta a tu base de datos)
host = "45.132.241.118"
port = 5432
dbname = "siginplan"
user = "juanyam"
password = "eJnNPmklNznIkZ1EJ8JB4B=="

# Conectar y leer
@st.cache_data(ttl=300)  # cachea por 5 minutos, puedes quitar si quieres en tiempo real puro
def cargar_datos():
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    query = "SELECT * FROM datos_trafico.tiempos_traslado_semaforos"
    df = pd.read_sql(query, conn)
    conn.close()
    return df




# Configuración en YAML
config = {
    'credentials': {
        'usernames': {
            'demo': {
                'name': 'demo',
                'password': '$2b$12$zZllcKwN4Pi0tYh9GJzHl.dtkfczvtDKe1G/nIBb5Uyk5hQW5kc9C'  # el hash que copiaste
            }
        }
    },
    'cookie': {
        'name': 'streamlit_auth',
        'key': 'abcdef',
        'expiry_days': 1
    }
}

# Crear objeto de autenticación
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login
name, authentication_status, username = authenticator.login("Iniciar sesión", "main")

if authentication_status:
    authenticator.logout("Cerrar sesión", "sidebar")
    st.sidebar.write(f"Bienvenido, {name}")

    opcion = st.sidebar.selectbox("Menú", ["Inicio", "Gráfica"])

    if opcion == "Inicio":
        st.title("Dashboard de prueba con login")
        st.write("Bienvenido al panel")

    elif opcion == "Gráfica":

        st.sidebar.header("Filtros")
        df = cargar_datos()
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['valor'] = 1
        df = df.groupby('Fecha')['valor'].sum().reset_index()
        df = df[['Fecha', 'valor']]

        # Obtener el día, mes y total de registros
        today = datetime.today()
        hoy = today.date()

        # Total del día (usando hoy)
        df_hoy = df[df['Fecha'].dt.date == hoy]
        total_dia = df_hoy['valor'].sum()

        # Total del mes (usando el mes actual)
        df_mes = df[df['Fecha'].dt.month == today.month]
        total_mes = df_mes['valor'].sum()

        # Total de registros
        total_registros = df['valor'].sum()

        fecha_max = pd.to_datetime(df['Fecha_Hora'].max())

        # Mostrar tarjetas con st.metric (tarjetas estáticas)
        st.title("Dashboard con métricas estáticas")

        # Crear tres columnas
        
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(label="Total del día", value=f"{total_dia}")

        with c2:
            st.metric(label="Total del mes", value=f"{total_mes}")

        with c3:
            st.metric(label="Total de registros", value=f"{total_registros}")

        with c4:
            st.metric(label="Última ejecución", value=f"{fecha_max}")
        

        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df['Día'] = df['Fecha'].dt.day
        df['Mes'] = df['Fecha'].dt.month
        meses_dict = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
              7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}
        df['Mes_nombre'] = df['Mes'].map(meses_dict)
        df['Año'] = df['Fecha'].dt.year

        # Sidebar de selección
        st.sidebar.header("Seleccionar tipo de acumulado")
        modo = st.sidebar.radio("Agrupar por", ["Mes (ver todos los días)", "Año (ver todos los meses)"])

        if modo == "Mes (ver todos los días)":
            meses_dict = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
              7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}
            mes = st.sidebar.selectbox("Mes", sorted(df['Mes'].map(meses_dict).unique()))
            año = st.sidebar.selectbox("Año", sorted(df['Año'].unique()))

            # Filtrar y agrupar por día
            df_mes = df[(df['Mes_nombre'] == mes) & (df['Año'] == año)]
            df_agg = df_mes.groupby('Día')['valor'].sum().reset_index()

            st.title(f"Acumulado diario en {mes} de {año}")
            fig = px.bar(df_agg, x='Día', y='valor', labels={'valor': 'Cantidad'}, title=f"Valores por día en {mes}")
            st.plotly_chart(fig, use_container_width=True)

        elif modo == "Año (ver todos los meses)":
            año = st.sidebar.selectbox("Año", sorted(df['Año'].unique()))

            # Filtrar y agrupar por mes
            df_año = df[df['Año'] == año]
            df_agg = df_año.groupby('Mes')['valor'].sum().reset_index()
            df_agg['Mes_nombre'] = df_agg['Mes'].map(meses_dict)
            df_agg = df_agg.sort_values('Mes')


            st.title(f"Acumulado mensual en {año}")
            fig = px.bar(df_agg, x='Mes_nombre', y='valor', labels={'valor': 'Cantidad'}, title=f"Valores por mes en {año}")
            st.plotly_chart(fig, use_container_width=True)

        #fecha_inicio = st.sidebar.date_input("Fecha inicio", df['Fecha'].min())
        #fecha_fin = st.sidebar.date_input("Fecha fin", df['Fecha'].max())

        #fecha_inicio = pd.Timestamp(fecha_inicio)
        #fecha_fin = pd.Timestamp(fecha_fin)

        #nivel = st.sidebar.selectbox("Nivel de agregación", ["Día", "Mes", "Año"])
        #df = df[(df['Fecha'] >= fecha_inicio) & (df['Fecha'] <= fecha_fin)]


        #if nivel == "Día":
        #    df_agg = df.groupby('Fecha')['valor'].sum().reset_index()
        #elif nivel == "Mes":
        #    df['Mes'] = df['Fecha'].dt.to_period('M').dt.to_timestamp()
        #    df_agg = df.groupby('Mes')['valor'].sum().reset_index()
        #    df_agg.rename(columns={'Mes': 'Fecha'}, inplace=True)
        #elif nivel == "Año":
        #    df['Año'] = df['Fecha'].dt.year
        #    df_agg = df.groupby('Año')['valor'].sum().reset_index()
        #    df_agg.rename(columns={'Año': 'Fecha'}, inplace=True)

        #st.title("Visualización por fecha")
        #st.write(f"Mostrando datos desde {fecha_inicio} hasta {fecha_fin}, agrupados por {nivel.lower()}")
        #fig = px.line(df_agg, x='Fecha', y='valor', title=f"Valores por {nivel.lower()}")
        #st.plotly_chart(fig, use_container_width=True)


        #st.title("Visualización por fecha")
        #st.write(f"Mostrando datos desde {fecha_inicio} hasta {fecha_fin}")
        #fig = px.line(df, x='Fecha', y='valor', title="Valores en el tiempo")
        #st.plotly_chart(fig, use_container_width=True)








        # Aplicar filtro
        #df_filtrado = df[(df['fecha'] >= pd.to_datetime(fecha_inicio)) & (df['fecha'] <= pd.to_datetime(fecha_fin))]
        # Mostrar gráfica
        #st.title("Visualización por fecha")
        #st.write(f"Mostrando datos desde {fecha_inicio} hasta {fecha_fin}")
        #fig = px.line(df_filtrado, x='fecha', y='valor', title="Valores en el tiempo")
        #st.plotly_chart(fig, use_container_width=True)

        #Datos de fechas
        #st.sidebar.header("Filtros")
        #fecha_inicio = st.sidebar.date_input("Fecha inicio", df['fecha'].min())
        #fecha_fin = st.sidebar.date_input("Fecha fin", df['fecha'].max())
        # Aplicar filtro
        #df_filtrado = df[(df['fecha'] >= pd.to_datetime(fecha_inicio)) & (df['fecha'] <= pd.to_datetime(fecha_fin))]
        # Mostrar gráfica
        #st.title("Visualización por fecha")
        #st.write(f"Mostrando datos desde {fecha_inicio} hasta {fecha_fin}")
        #fig = px.line(df_filtrado, x='fecha', y='valor', title="Valores en el tiempo")
        #st.plotly_chart(fig, use_container_width=True)

        # Datos en graficas de barras
        #df = pd.DataFrame({"Categoría": ["A", "B", "C"], "Valor": [10, 20, 15]})
        #fig = px.bar(df, x="Categoría", y="Valor")
        #st.plotly_chart(fig)

        # Mostrar los datos
        #Graficas en tablas
        #st.title("Dashboard en tiempo real desde PostgreSQL")
        #df = cargar_datos()
        #st.write(df)

elif authentication_status is False:
    st.error("Usuario o contraseña incorrectos")
elif authentication_status is None:
    st.warning("Introduce tus credenciales")








