# app_web.py - Dashboard Mejorado con Sistema de Pagos y Notificaciones (SEGURA)
import streamlit as st
import pandas as pd
import requests
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title="Gestión Gimnasio",
    page_icon="",
    layout="wide"
)

# Título principal
st.title(" Dashboard - Gestión del Gimnasio")
st.markdown("---")

# ========== FUNCIONES PARA OBTENER DATOS ==========
def obtener_todos_socios():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/socios/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")
        return pd.DataFrame()

def obtener_entradas():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/entradas/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def obtener_reservas():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/reservas/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def obtener_clases():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/clases/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def obtener_planes():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/planes/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def obtener_pagos():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/pagos/")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def obtener_reporte_ingresos(año: int = None):
    try:
        url = "https://gimnasio-2-0-1.onrender.com/reportes/ingresos-mensuales"
        if año:
            url += f"?año={año}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        return {}

def obtener_reporte_asistencia(mes: int = None, año: int = None):
    try:
        url = "https://gimnasio-2-0-1.onrender.com/reportes/asistencia-horarios"
        params = {}
        if mes:
            params['mes'] = mes
        if año:
            params['año'] = año
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        return {}

def obtener_reporte_instructores():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/reportes/popularidad-instructores")
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        return {}

def obtener_vencimientos_proximos(dias: int = 3):
    """Obtiene socios con vencimientos próximos"""
    try:
        url = f"https://gimnasio-2-0-1.onrender.com/notificaciones/vencimientos-proximos?dias={dias}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {}
    except Exception as e:
        return {}

def enviar_notificacion_individual(socio_id: str):
    """Envía una notificación individual a un socio"""
    try:
        url = f"https://gimnasio-2-0-1.onrender.com/notificaciones/enviar-recordatorio?socio_id={socio_id}"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error de API: {response.status_code}"}
    except Exception as e:
        return {"error": f"Error de conexión: {str(e)}"}

# ========== INTERFAZ PRINCIPAL ==========
# Sidebar para navegación
st.sidebar.title("Navegación")
opcion = st.sidebar.selectbox(
    "Selecciona una sección:",
    ["Dashboard", "Gestión de Socios", "Pagos", "Clases", "Entradas", "Reservas", "Reportes", " Notificaciones"]
)

if opcion == "Dashboard":
    st.header(" Dashboard de Métricas")
    # Obtener datos
    df_socios = obtener_todos_socios()
    df_entradas = obtener_entradas()
    df_reservas = obtener_reservas()
    df_clases = obtener_clases()
    
    # ========== MÉTRICAS VISUALES MEJORADAS ==========
    st.subheader(" Métricas en Tiempo Real")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # MÉTRICA 1: Total Socios
        total_socios = len(df_socios) if not df_socios.empty else 0
        if not df_socios.empty and 'vencimiento' in df_socios.columns:
            try:
                socios_nuevos = sum(pd.to_datetime(df_socios['vencimiento'], errors='coerce') >= pd.Timestamp(datetime.now().date() - timedelta(days=30)))
            except:
                socios_nuevos = 0
        else:
            socios_nuevos = 0
        # Determinar icono según crecimiento
        if socios_nuevos >= 5:
            icono = ""
        elif socios_nuevos >= 2:
            icono = ""
        else:
            icono = ""
        st.metric(
            label=f"{icono} Total Socios",
            value=total_socios,
            delta=f"+{socios_nuevos} nuevos (30d)",
            delta_color="normal"
        )
        st.caption("Socios registrados en el sistema")
    
    with col2:
        # MÉTRICA 2: Entradas 7 Días
        if not df_entradas.empty:
            df_entradas['fecha'] = pd.to_datetime(df_entradas['fecha_hora']).dt.date
            hoy = datetime.now().date()
            semana_actual = df_entradas[df_entradas['fecha'] >= hoy - timedelta(days=7)]
            semana_pasada = df_entradas[(df_entradas['fecha'] >= hoy - timedelta(days=14)) & 
                                       (df_entradas['fecha'] < hoy - timedelta(days=7))]
            
            entradas_semana_actual = len(semana_actual)
            entradas_semana_pasada = len(semana_pasada)
            
            # Calcular diferencia
            if entradas_semana_pasada > 0:
                diferencia = entradas_semana_actual - entradas_semana_pasada
                porcentaje = (diferencia / entradas_semana_pasada) * 100
                delta_text = f"{diferencia:+.0f} ({porcentaje:+.0f}%)"
            else:
                delta_text = f"+{entradas_semana_actual}"
            
            # Determinar icono según actividad
            if entradas_semana_actual >= 20:
                icono = ""
            elif entradas_semana_actual >= 10:
                icono = ""
            else:
                icono = ""
            
            st.metric(
                label=f"{icono} Entradas 7 Días",
                value=entradas_semana_actual,
                delta=delta_text,
                delta_color="normal"
            )
            st.caption("Comparado con la semana anterior")
        else:
            st.metric(
                label=" Entradas 7 Días",
                value=0
            )
            st.caption("No hay datos de entradas")
    
    with col3:
        # MÉTRICA 3: Reservas Activas
        reservas_activas = len(df_reservas[df_reservas['estado'] == 'confirmada']) if not df_reservas.empty else 0
        
        # Calcular ocupación
        if not df_clases.empty and not df_reservas.empty:
            capacidad_total = df_clases['capacidad_max'].sum()
            reservas_totales = len(df_reservas[df_reservas['estado'] == 'confirmada'])
            ocupacion = (reservas_totales / capacidad_total * 100) if capacidad_total > 0 else 0
            
            # Determinar icono según ocupación
            if ocupacion >= 80:
                icono = ""
            elif ocupacion >= 60:
                icono = ""
            else:
                icono = ""
            
            st.metric(
                label=f"{icono} Reservas Activas",
                value=reservas_activas,
                delta=f"{ocupacion:.0f}% ocupación",
                delta_color="normal"
            )
            st.caption(f"De {capacidad_total} cupos totales")
        else:
            st.metric(
                label=" Reservas Activas",
                value=reservas_activas
            )
            st.caption("No hay datos de capacidad")
    
    with col4:
        # MÉTRICA 4: Clases Disponibles
        total_clases = len(df_clases) if not df_clases.empty else 0
        if not df_clases.empty:
            clases_por_dia = df_clases['dia_semana'].nunique()
            
            # Determinar icono según variedad
            if clases_por_dia >= 5:
                icono = ""
            elif clases_por_dia >= 3:
                icono = ""
            else:
                icono = ""
            
            st.metric(
                label=f"{icono} Clases Disponibles",
                value=total_clases,
                delta=f"{clases_por_dia} días/semana",
                delta_color="normal"
            )
            st.caption("Distribución semanal")
        else:
            st.metric(
                label=" Clases Disponibles",
                value=total_clases
            )
            st.caption("No hay clases programadas")
    
    # ========== SISTEMA DE ALERTAS AUTOMÁTICAS ==========
    st.subheader(" Alertas del Sistema")
    
    # Contador de alertas
    alertas_totales = 0
    alertas_items = []
    
    # ALERTA 1: Membresías próximas a vencer (3 días)
    if not df_socios.empty:
        hoy = datetime.now().date()
        try:
            # Filtrar socios con membresías válidas
            df_socios_validos = df_socios[df_socios['vencimiento'] != 'string']
            fechas_vencimiento = pd.to_datetime(df_socios_validos['vencimiento'], errors='coerce')
            # Calcular días hasta vencimiento
            dias_hasta_vencer = (fechas_vencimiento - pd.Timestamp(hoy)).dt.days
            # Encontrar membresías que vencen en 3 días o menos
            membresias_proximas = df_socios_validos[
                (dias_hasta_vencer >= 0) & (dias_hasta_vencer <= 3)
            ]
            if not membresias_proximas.empty:
                alertas_totales += len(membresias_proximas)
                for _, socio in membresias_proximas.iterrows():
                    dias = (pd.to_datetime(socio['vencimiento']) - pd.Timestamp(hoy)).days
                    if dias == 0:
                        mensaje = f" **HOY** - {socio['nombre']} (ID: {socio['id']})"
                    elif dias == 1:
                        mensaje = f" **1 día** - {socio['nombre']} (ID: {socio['id']})"
                    else:
                        mensaje = f" **{dias} días** - {socio['nombre']} (ID: {socio['id']})"
                    alertas_items.append(mensaje)
        except:
            pass
    
    # ALERTA 2: Clases con alta demanda (>80% ocupación)
    if not df_clases.empty and not df_reservas.empty:
        for _, clase in df_clases.iterrows():
            reservas_clase = len(df_reservas[
                (df_reservas['clase_id'] == clase['id']) & 
                (df_reservas['estado'] == 'confirmada')
            ])
            ocupacion = (reservas_clase / clase['capacidad_max']) * 100 if clase['capacidad_max'] > 0 else 0
            if ocupacion >= 80:
                alertas_totales += 1
                alertas_items.append(f" **Clase llena** - {clase['nombre']} ({ocupacion:.0f}% ocupada)")
            elif ocupacion >= 60:
                alertas_totales += 1
                alertas_items.append(f" **Alta demanda** - {clase['nombre']} ({ocupacion:.0f}% ocupada)")
    
    # ALERTA 3: Socios inactivos (sin entrada en 30 días)
    if not df_socios.empty and not df_entradas.empty:
        df_entradas['fecha'] = pd.to_datetime(df_entradas['fecha_hora']).dt.date
        fecha_limite = hoy - timedelta(days=30)
        # Encontrar última entrada de cada socio
        ultimas_entradas = df_entradas.groupby('socio_id')['fecha'].max()
        for _, socio in df_socios.iterrows():
            if socio['id'] in ultimas_entradas:
                ultima_entrada = ultimas_entradas[socio['id']]
                if ultima_entrada < fecha_limite:
                    alertas_totales += 1
                    dias_inactivo = (hoy - ultima_entrada).days
                    alertas_items.append(f" **Inactivo** - {socio['nombre']} ({dias_inactivo} días sin venir)")
    
    # Mostrar alertas
    if alertas_totales > 0:
        # Badge con número de alertas
        st.warning(f" Tienes **{alertas_totales}** alertas pendientes")
        # Mostrar cada alerta en una tarjeta
        for alerta in alertas_items:
            st.write(alerta)
    else:
        st.success(" No hay alertas pendientes - ¡Todo está bajo control!")
    
    st.markdown("---")
    
    # ========== GRÁFICOS ==========
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader(" Distribución de Clases")
        if not df_clases.empty:
            # Gráfico de torta - Clases por día
            clase_count = df_clases['dia_semana'].value_counts()
            fig_clases = px.pie(
                values=clase_count.values,
                names=clase_count.index,
                title="Clases por Día de la Semana"
            )
            st.plotly_chart(fig_clases, use_container_width=True)
        else:
            st.info("No hay datos de clases disponibles")
    
    with col_right:
        st.subheader(" Entradas por Día")
        if not df_entradas.empty:
            # Convertir fecha_hora a datetime y extraer fecha
            df_entradas['fecha'] = pd.to_datetime(df_entradas['fecha_hora']).dt.date
            entradas_por_dia = df_entradas['fecha'].value_counts().sort_index()
            fig_entradas = px.bar(
                x=entradas_por_dia.index.astype(str),
                y=entradas_por_dia.values,
                title="Entradas Registradas por Día",
                labels={'x': 'Fecha', 'y': 'Número de Entradas'}
            )
            st.plotly_chart(fig_entradas, use_container_width=True)
        else:
            st.info("No hay datos de entradas disponibles")
    
    # ========== GRÁFICO DE TENDENCIA SEMANAL ==========
    st.subheader(" Tendencia de Asistencia Semanal")
    if not df_entradas.empty:
        # Preparar datos para el gráfico de tendencia
        df_entradas['fecha'] = pd.to_datetime(df_entradas['fecha_hora']).dt.date
        df_entradas['dia_semana'] = pd.to_datetime(df_entradas['fecha_hora']).dt.day_name()
        df_entradas['hora'] = pd.to_datetime(df_entradas['fecha_hora']).dt.hour
        
        # Crear datos para las últimas 2 semanas
        hoy = datetime.now().date()
        inicio_semana_actual = hoy - timedelta(days=hoy.weekday())
        inicio_semana_pasada = inicio_semana_actual - timedelta(days=7)
        
        # Filtrar datos de las últimas 2 semanas
        datos_semana_actual = df_entradas[df_entradas['fecha'] >= inicio_semana_actual]
        datos_semana_pasada = df_entradas[
            (df_entradas['fecha'] >= inicio_semana_pasada) & 
            (df_entradas['fecha'] < inicio_semana_actual)
        ]
        
        # Contar entradas por día para cada semana
        tendencia_actual = datos_semana_actual['fecha'].value_counts().sort_index()
        tendencia_pasada = datos_semana_pasada['fecha'].value_counts().sort_index()
        
        # Crear gráfico de líneas comparativo
        fig_tendencia = go.Figure()
        
        # Línea de la semana actual
        if not tendencia_actual.empty:
            fig_tendencia.add_trace(go.Scatter(
                x=tendencia_actual.index.astype(str),
                y=tendencia_actual.values,
                mode='lines+markers',
                name='Semana Actual',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ))
        
        # Línea de la semana pasada
        if not tendencia_pasada.empty:
            fig_tendencia.add_trace(go.Scatter(
                x=tendencia_pasada.index.astype(str),
                y=tendencia_pasada.values,
                mode='lines+markers',
                name='Semana Pasada',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                marker=dict(size=6)
            ))
        
        fig_tendencia.update_layout(
            title="Evolución de Asistencia - Últimas 2 Semanas",
            xaxis_title="Fecha",
            yaxis_title="Número de Entradas",
            hovermode='x unified',
            showlegend=True
        )
        st.plotly_chart(fig_tendencia, use_container_width=True)
        
        # Estadísticas rápidas de la tendencia
        if not tendencia_actual.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                promedio_actual = tendencia_actual.mean()
                st.metric("Promedio Semanal", f"{promedio_actual:.1f} entradas/día")
            with col2:
                if not tendencia_pasada.empty:
                    crecimiento = ((tendencia_actual.sum() - tendencia_pasada.sum()) / tendencia_pasada.sum() * 100)
                    st.metric("Crecimiento", f"{crecimiento:+.1f}%")
                else:
                    st.metric("Crecimiento", "Nuevo")
            with col3:
                dia_pico = tendencia_actual.idxmax().strftime('%A') if not tendencia_actual.empty else "N/A"
                st.metric("Día Más Activo", dia_pico)
    else:
        st.info("No hay suficientes datos para mostrar tendencia")
    
    # ========== TABLA DE ACTIVIDAD RECIENTE ==========
    st.subheader(" Actividad Reciente")
    if not df_entradas.empty:
        # Mostrar últimas 5 entradas
        df_recent = df_entradas.sort_values('fecha_hora', ascending=False).head(5)
        st.dataframe(df_recent[['nombre_socio', 'fecha_hora']], use_container_width=True)
    else:
        st.info("No hay actividad reciente para mostrar")

elif opcion == "Gestión de Socios":
    st.header(" Gestión de Socios")
    df_socios = obtener_todos_socios()
    if not df_socios.empty:
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Socios", len(df_socios))
        with col2:
            st.metric("IDs Únicos", df_socios['id'].nunique())
        with col3:
            # Calcular socios con membresía vigente (manejo seguro de errores)
            hoy = datetime.now().date()
            try:
                # Filtrar solo fechas válidas, ignorar errores
                fechas_validas = pd.to_datetime(df_socios['vencimiento'], errors='coerce')
                socios_vigentes = sum(fechas_validas >= pd.Timestamp(hoy))
                st.metric("Membresías Vigentes", socios_vigentes)
            except Exception as e:
                st.metric("Membresías Vigentes", "N/A")
        
        st.subheader("Lista de Socios")
        st.dataframe(df_socios, use_container_width=True)
        
        # Formulario para añadir nuevo socio
        st.subheader(" Añadir Nuevo Socio")
        with st.form("nuevo_socio"):
            col1, col2, col3 = st.columns(3)
            with col1:
                nuevo_id = st.text_input("ID del Socio")
            with col2:
                nuevo_nombre = st.text_input("Nombre Completo")
            with col3:
                nuevo_vencimiento = st.date_input("Fecha de Vencimiento")
            
            if st.form_submit_button("Crear Socio"):
                if nuevo_id and nuevo_nombre:
                    try:
                        response = requests.post(
                            "https://gimnasio-2-0-1.onrender.com/socios/",
                            json={
                                "id": nuevo_id,
                                "nombre": nuevo_nombre,
                                "vencimiento": str(nuevo_vencimiento)
                            }
                        )
                        if response.status_code == 200:
                            st.success(" Socio creado exitosamente")
                            st.rerun()
                        else:
                            st.error(f" Error: {response.json().get('detail', 'Error desconocido')}")
                    except Exception as e:
                        st.error(f" Error de conexión: {e}")
                else:
                    st.warning(" Completa todos los campos")
    else:
        st.warning("No hay socios registrados o no se pudo conectar a la API")

elif opcion == "Pagos":
    st.header(" Gestión de Pagos y Facturación")
    # Obtener datos
    df_planes = obtener_planes()
    df_pagos = obtener_pagos()
    df_socios = obtener_todos_socios()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(" Planes de Membresía")
        if not df_planes.empty:
            # Mostrar planes con formato mejorado
            for _, plan in df_planes.iterrows():
                with st.container():
                    st.markdown(f"**{plan['nombre']}** - ")
                    st.caption(f"{plan['descripcion']} ({plan['duracion_dias']} días)")
                    st.progress(1.0 if plan['activo'] else 0.0)
        else:
            st.info("No hay planes disponibles")
    
    with col2:
        st.subheader(" Registrar Nuevo Pago")
        with st.form("registrar_pago"):
            if not df_socios.empty and not df_planes.empty:
                socio_seleccionado = st.selectbox(
                    "Socio", 
                    options=[f"{s['id']} - {s['nombre']}" for s in df_socios.to_dict('records')]
                )
                plan_seleccionado = st.selectbox(
                    "Plan",
                    options=[f"{p['id']} - {p['nombre']} ()" for p in df_planes.to_dict('records')]
                )
                metodo_pago = st.selectbox("Método de Pago", ["efectivo", "tarjeta", "transferencia"])
                
                if st.form_submit_button(" Registrar Pago"):
                    # Extraer IDs
                    socio_id = socio_seleccionado.split(" - ")[0]
                    plan_id = plan_seleccionado.split(" - ")[0]
                    try:
                        response = requests.post(
                            f"https://gimnasio-2-0-1.onrender.com/pagos/?socio_id={socio_id}&plan_id={plan_id}&metodo_pago={metodo_pago}"
                        )
                        if response.status_code == 200:
                            st.success(" Pago registrado exitosamente!")
                            st.balloons()
                        else:
                            st.error(f" Error: {response.json().get('detail', 'Error desconocido')}")
                    except Exception as e:
                        st.error(f" Error de conexión: {e}")
            else:
                st.warning("Necesitas socios y planes para registrar pagos")
    
    st.subheader(" Historial de Pagos")
    if not df_pagos.empty:
        # Mostrar métricas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Pagos", len(df_pagos))
        with col2:
            st.metric("Ingresos Totales", f"")
        with col3:
            st.metric("Promedio por Pago", f"")
        
        # Mostrar tabla de pagos
        st.dataframe(df_pagos, use_container_width=True)
    else:
        st.info("No hay pagos registrados aún")

elif opcion == "Clases":
    st.header(" Gestión de Clases")
    df_clases = obtener_clases()
    if not df_clases.empty:
        st.dataframe(df_clases, use_container_width=True)
        # Estadísticas de clases
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Clases", len(df_clases))
        with col2:
            st.metric("Días con clases", df_clases['dia_semana'].nunique())
    else:
        st.error("Error al obtener las clases")

elif opcion == "Entradas":
    st.header(" Registro de Entradas")
    st.subheader("Registrar entrada de socio")
    socio_id_entrada = st.text_input("ID del socio", key="entrada_id")
    if st.button("Registrar entrada"):
        if socio_id_entrada.strip():
            try:
                response = requests.post(
                    "https://gimnasio-2-0-1.onrender.com/entradas/?socio_id=" + socio_id_entrada.strip()
                )
                if response.status_code == 200:
                    entrada_data = response.json()
                    st.success(f" Entrada registrada para {entrada_data['nombre_socio']} a las {entrada_data['fecha_hora']}")
                else:
                    st.error(" Error al registrar la entrada")
            except Exception as e:
                st.error(f" Error de conexión: {e}")
        else:
            st.warning("Por favor, ingresa un ID válido")
    
    # Mostrar historial de entradas
    st.subheader(" Historial de Entradas")
    df_entradas = obtener_entradas()
    if not df_entradas.empty:
        st.dataframe(df_entradas, use_container_width=True)
    else:
        st.info("No hay entradas registradas")

elif opcion == "Reservas":
    st.header(" Gestión de Reservas")
    st.subheader("Reservar clase")
    socio_id_reserva = st.text_input("ID del socio", key="reserva_socio_id")
    # Obtener clases disponibles
    df_clases = obtener_clases()
    if not df_clases.empty:
        clase_options = {f"{c['nombre']} - {c['dia_semana']} {c['hora_inicio']}": c['id'] for c in df_clases.to_dict('records')}
        clase_seleccionada = st.selectbox("Clase", list(clase_options.keys()))
        clase_id = clase_options[clase_seleccionada]
    else:
        st.warning("No hay clases disponibles")
        clase_id = None
    
    if st.button("Crear reserva"):
        if socio_id_reserva.strip() and clase_id is not None:
            try:
                response = requests.post(
                    f"https://gimnasio-2-0-1.onrender.com/reservas/?socio_id={socio_id_reserva.strip()}&clase_id={clase_id}"
                )
                if response.status_code == 200:
                    reserva_data = response.json()
                    st.success(f" Reserva confirmada para clase ID {reserva_data['clase_id']}")
                else:
                    error_detail = response.json().get('detail', 'Error desconocido')
                    st.error(f" Error: {error_detail}")
            except Exception as e:
                st.error(f" Error de conexión: {e}")
        else:
            st.warning("Completa todos los campos")
    
    # Mostrar reservas activas
    st.subheader(" Reservas Activas")
    df_reservas = obtener_reservas()
    if not df_reservas.empty:
        reservas_activas = df_reservas[df_reservas['estado'] == 'confirmada']
        st.dataframe(reservas_activas, use_container_width=True)
    else:
        st.info("No hay reservas activas")

elif opcion == "Reportes":
    st.header(" Reportes Ejecutivos Automáticos")
    # Obtener datos para reportes antiguos
    df_entradas = obtener_entradas()
    df_socios = obtener_todos_socios()
    df_reservas = obtener_reservas()
    df_clases = obtener_clases()
    df_pagos = obtener_pagos()
    
    # Selector de tipo de reporte MEJORADO
    tipo_reporte = st.selectbox(
        "Selecciona el tipo de reporte:",
        [
            " Reporte de Ingresos", 
            " Análisis de Asistencia", 
            " Popularidad de Instructores",
            " Resumen Semanal",
            " Análisis de Horarios", 
            " Tendencias Mensuales",
            " Socios Más Activos",
            " Reporte de Ingresos (Avanzado)"
        ]
    )
    
    if tipo_reporte == " Reporte de Ingresos":
        st.subheader(" Reporte de Ingresos Mensuales")
        # Selector de año
        año_actual = datetime.now().year
        año_seleccionado = st.selectbox("Año", options=[año_actual, año_actual-1, año_actual-2])
        # Obtener reporte
        reporte = obtener_reporte_ingresos(año_seleccionado)
        if reporte and 'ingresos_totales' in reporte:
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Ingresos Totales", f"")
            with col2:
                st.metric("Total Pagos", reporte['total_pagos'])
            with col3:
                st.metric("Promedio por Pago", f"")
            with col4:
                crecimiento = "" if reporte['total_pagos'] > 0 else ""
                st.metric("Estado", crecimiento)
            
            # Gráfico de ingresos mensuales
            if reporte['ingresos_mensuales']:
                meses = list(reporte['ingresos_mensuales'].keys())
                ingresos = list(reporte['ingresos_mensuales'].values())
                # Convertir números de mes a nombres
                nombres_meses = [datetime(2023, int(mes), 1).strftime('%B') for mes in meses]
                fig_ingresos = px.bar(
                    x=nombres_meses,
                    y=ingresos,
                    title=f"Ingresos Mensuales - Año {año_seleccionado}",
                    labels={'x': 'Mes', 'y': 'Ingresos ($)'},
                    color=ingresos,
                    color_continuous_scale='greens'
                )
                st.plotly_chart(fig_ingresos, use_container_width=True)
            
            # Planes más populares
            if reporte['planes_populares']:
                st.subheader(" Planes Más Populares")
                planes_data = []
                for plan_id, cantidad in reporte['planes_populares'].items():
                    # Obtener nombre del plan
                    planes = obtener_planes()
                    plan_nombre = "Desconocido"
                    if not planes.empty:
                        plan_info = planes[planes['id'] == int(plan_id)]
                        if not plan_info.empty:
                            plan_nombre = plan_info.iloc[0]['nombre']
                    planes_data.append({"Plan": f"{plan_nombre} (ID: {plan_id})", "Ventas": cantidad})
                df_planes = pd.DataFrame(planes_data)
                fig_planes = px.pie(
                    df_planes, 
                    values='Ventas', 
                    names='Plan',
                    title="Distribución de Planes Vendidos"
                )
                st.plotly_chart(fig_planes, use_container_width=True)
        else:
            st.info("No hay datos de ingresos para el año seleccionado")
    
    elif tipo_reporte == " Análisis de Asistencia":
        st.subheader(" Análisis de Asistencia por Horarios")
        # Selectores de fecha
        col1, col2 = st.columns(2)
        with col1:
            mes_seleccionado = st.selectbox("Mes", options=list(range(1, 13)), format_func=lambda x: datetime(2023, x, 1).strftime('%B'))
        with col2:
            año_seleccionado = st.selectbox("Año", options=[2024, 2025, 2026])
        # Obtener reporte
        reporte = obtener_reporte_asistencia(mes_seleccionado, año_seleccionado)
        if reporte and 'total_entradas' in reporte:
            # Métricas principales
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Entradas", reporte['total_entradas'])
            with col2:
                st.metric("Hora Pico", f"{reporte['hora_pico']:02d}:00" if reporte['hora_pico'] else "N/A")
            with col3:
                st.metric("Día Más Activo", reporte['dia_mas_activo'] if reporte['dia_mas_activo'] else "N/A")
            
            # Gráfico de asistencia por hora
            if reporte['asistencia_por_hora']:
                horas = [f"{h:02d}:00" for h in reporte['asistencia_por_hora'].keys()]
                asistencias = list(reporte['asistencia_por_hora'].values())
                fig_horas = px.bar(
                    x=horas,
                    y=asistencias,
                    title="Asistencia por Hora del Día",
                    labels={'x': 'Hora', 'y': 'Número de Entradas'},
                    color=asistencias,
                    color_continuous_scale='blues'
                )
                st.plotly_chart(fig_horas, use_container_width=True)
            
            # Socios más activos
            if reporte['socios_mas_activos']:
                st.subheader(" Top 10 Socios Más Activos")
                socios_data = []
                for socio, visitas in reporte['socios_mas_activos'].items():
                    socios_data.append({"Socio": socio, "Visitas": visitas})
                df_socios = pd.DataFrame(socios_data)
                fig_socios = px.bar(
                    df_socios,
                    x='Visitas',
                    y='Socio',
                    orientation='h',
                    title="Socios Más Activos del Mes",
                    color='Visitas',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_socios, use_container_width=True)
        else:
            st.info("No hay datos de asistencia para el período seleccionado")
    
    elif tipo_reporte == " Popularidad de Instructores":
        st.subheader(" Popularidad de Instructores")
        # Obtener reporte
        reporte = obtener_reporte_instructores()
        if reporte and 'popularidad_instructores' in reporte:
            # Métricas principales
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Reservas Analizadas", reporte['total_reservas_analizadas'])
            with col2:
                instructor_top = max(reporte['popularidad_instructores'].items(), key=lambda x: x[1]) if reporte['popularidad_instructores'] else ("N/A", 0)
                st.metric("Instructor Más Popular", f"{instructor_top[0]} ({instructor_top[1]} clases)")
            
            # Gráfico de popularidad de instructores
            if reporte['popularidad_instructores']:
                instructores = list(reporte['popularidad_instructores'].keys())
                clases = list(reporte['popularidad_instructores'].values())
                fig_instructores = px.bar(
                    x=clases,
                    y=instructores,
                    orientation='h',
                    title="Popularidad de Instructores",
                    labels={'x': 'Número de Clases', 'y': 'Instructor'},
                    color=clases,
                    color_continuous_scale='reds'
                )
                st.plotly_chart(fig_instructores, use_container_width=True)
            
            # Clases más populares
            if reporte['clases_populares']:
                st.subheader(" Clases Más Populares")
                clases_data = []
                for clase, reservas in reporte['clases_populares'].items():
                    clases_data.append({"Clase": clase, "Reservas": reservas})
                df_clases = pd.DataFrame(clases_data)
                fig_clases = px.pie(
                    df_clases,
                    values='Reservas',
                    names='Clase',
                    title="Distribución de Clases Más Populares"
                )
                st.plotly_chart(fig_clases, use_container_width=True)
        else:
            st.info("No hay datos de instructores disponibles")
    
    # === REPORTES ANTIGUOS (MANTENIDOS) ===
    elif tipo_reporte == " Resumen Semanal":
        st.subheader(" Reporte Semanal de Actividad")
        if not df_entradas.empty:
            # Procesar datos de la semana
            df_entradas['fecha'] = pd.to_datetime(df_entradas['fecha_hora']).dt.date
            df_entradas['dia_semana'] = pd.to_datetime(df_entradas['fecha_hora']).dt.day_name()
            df_entradas['hora'] = pd.to_datetime(df_entradas['fecha_hora']).dt.hour
            hoy = datetime.now().date()
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            datos_semana = df_entradas[df_entradas['fecha'] >= inicio_semana]
            if not datos_semana.empty:
                # Estadísticas semanales
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_entradas = len(datos_semana)
                    st.metric("Entradas Totales", total_entradas)
                with col2:
                    socios_unicos = datos_semana['socio_id'].nunique()
                    st.metric("Socios Únicos", socios_unicos)
                with col3:
                    promedio_diario = total_entradas / datos_semana['fecha'].nunique()
                    st.metric("Promedio Diario", f"{promedio_diario:.1f}")
                
                # Gráfico de entradas por día de la semana
                entradas_por_dia = datos_semana['dia_semana'].value_counts()
                # Ordenar días de la semana
                orden_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                entradas_ordenadas = entradas_por_dia.reindex(orden_dias, fill_value=0)
                fig_semana = px.bar(
                    x=[ 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
                    y=entradas_ordenadas.values,
                    title="Entradas por Día de la Semana",
                    labels={'x': 'Día', 'y': 'Número de Entradas'},
                    color=entradas_ordenadas.values,
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_semana, use_container_width=True)
                
                # Top 5 socios más activos de la semana
                st.subheader(" Top 5 Socios Más Activos")
                socios_activos = datos_semana['nombre_socio'].value_counts().head(5)
                for i, (socio, count) in enumerate(socios_activos.items(), 1):
                    st.write(f"{i}. **{socio}** - {count} entradas")
            else:
                st.info("No hay datos de esta semana")
        else:
            st.info("No hay datos de entradas para generar el reporte")
    
    elif tipo_reporte == " Análisis de Horarios":
        st.subheader(" Análisis de Horarios Populares")
        if not df_entradas.empty:
            df_entradas['hora'] = pd.to_datetime(df_entradas['fecha_hora']).dt.hour
            # Distribución por horarios
            entradas_por_hora = df_entradas['hora'].value_counts().sort_index()
            fig_horarios = px.bar(
                x=[f"{h:02d}:00" for h in entradas_por_hora.index],
                y=entradas_por_hora.values,
                title="Entradas por Hora del Día",
                labels={'x': 'Hora', 'y': 'Número de Entradas'},
                color=entradas_por_hora.values,
                color_continuous_scale='reds'
            )
            st.plotly_chart(fig_horarios, use_container_width=True)
            
            # Horario pico
            hora_pico = entradas_por_hora.idxmax()
            st.metric(" Horario Más Popular", f"{hora_pico:02d}:00")
        else:
            st.info("No hay datos de entradas para analizar horarios")
    
    elif tipo_reporte == " Tendencias Mensuales":
        st.subheader(" Tendencias Mensuales")
        if not df_entradas.empty:
            df_entradas['mes'] = pd.to_datetime(df_entradas['fecha_hora']).dt.to_period('M')
            tendencia_mensual = df_entradas['mes'].value_counts().sort_index()
            fig_tendencia = px.line(
                x=tendencia_mensual.index.astype(str),
                y=tendencia_mensual.values,
                title="Evolución Mensual de Asistencia",
                labels={'x': 'Mes', 'y': 'Entradas Totales'},
                markers=True
            )
            st.plotly_chart(fig_tendencia, use_container_width=True)
            
            # Cálculo de crecimiento
            if len(tendencia_mensual) >= 2:
                ultimo_mes = tendencia_mensual.iloc[-1]
                mes_anterior = tendencia_mensual.iloc[-2]
                crecimiento = ((ultimo_mes - mes_anterior) / mes_anterior) * 100
                st.metric("Crecimiento Mensual", f"{crecimiento:+.1f}%")
        else:
            st.info("No hay suficientes datos para mostrar tendencias")
    
    elif tipo_reporte == " Socios Más Activos":
        st.subheader(" Socios Más Activos - Histórico")
        if not df_entradas.empty:
            # Top 10 socios más activos de todos los tiempos
            socios_activos = df_entradas['nombre_socio'].value_counts().head(10)
            fig_socios = px.bar(
                x=socios_activos.values,
                y=socios_activos.index,
                orientation='h',
                title="Top 10 Socios Más Activos",
                labels={'x': 'Total de Entradas', 'y': 'Socio'},
                color=socios_activos.values,
                color_continuous_scale='greens'
            )
            st.plotly_chart(fig_socios, use_container_width=True)
            
            # Estadísticas de fidelidad
            st.subheader(" Estadísticas de Fidelidad")
            col1, col2 = st.columns(2)
            with col1:
                promedio_entradas = socios_activos.mean()
                st.metric("Promedio de Entradas", f"{promedio_entradas:.1f}")
            with col2:
                socio_top = socios_activos.index[0]
                entradas_top = socios_activos.iloc[0]
                st.metric("Socio Más Fiel", f"{socio_top} ({entradas_top} entradas)")
        else:
            st.info("No hay datos de entradas para analizar socios")
    
    elif tipo_reporte == " Reporte de Ingresos (Avanzado)":
        st.subheader(" Reporte de Ingresos Avanzado")
        if not df_pagos.empty:
            # Métricas de ingresos
            col1, col2, col3 = st.columns(3)
            with col1:
                ingresos_totales = df_pagos['monto'].sum()
                st.metric("Ingresos Totales", f"")
            with col2:
                promedio_pago = df_pagos['monto'].mean()
                st.metric("Promedio por Pago", f"")
            with col3:
                total_pagos = len(df_pagos)
                st.metric("Total de Pagos", total_pagos)
            
            # Gráfico de ingresos por mes
            df_pagos['mes'] = pd.to_datetime(df_pagos['fecha_pago']).dt.to_period('M')
            ingresos_mensuales = df_pagos.groupby('mes')['monto'].sum()
            if not ingresos_mensuales.empty:
                fig_ingresos = px.line(
                    x=ingresos_mensuales.index.astype(str),
                    y=ingresos_mensuales.values,
                    title="Evolución de Ingresos Mensuales",
                    labels={'x': 'Mes', 'y': 'Ingresos ($)'},
                    markers=True
                )
                st.plotly_chart(fig_ingresos, use_container_width=True)
            
            # Métodos de pago más populares
            st.subheader(" Métodos de Pago")
            metodos_pago = df_pagos['metodo_pago'].value_counts()
            fig_metodos = px.pie(
                values=metodos_pago.values,
                names=metodos_pago.index,
                title="Distribución por Método de Pago"
            )
            st.plotly_chart(fig_metodos, use_container_width=True)
        else:
            st.info("No hay datos de pagos para generar el reporte")

elif opcion == " Notificaciones":
    st.header(" Sistema de Notificaciones Automáticas")
    
    st.subheader(" Estado de Notificaciones")
    # Obtener vencimientos próximos
    vencimientos = obtener_vencimientos_proximos(dias=3)
    
    if vencimientos and 'vencimientos' in vencimientos:
        total_vencimientos = vencimientos.get('total_vencimientos', 0)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Socios con Vencimiento Próximo", total_vencimientos)
        with col2:
            st.metric("Días de Alerta", vencimientos.get('dias_anticipacion', 3))
        with col3:
            st.metric("Fecha Consulta", vencimientos.get('fecha_consulta', 'N/A'))
        
        if total_vencimientos > 0:
            st.subheader(" Socios con Vencimiento Próximo")
            vencimientos_df = pd.DataFrame(vencimientos['vencimientos'])
            st.dataframe(vencimientos_df, use_container_width=True)
            
            # Botón para enviar notificaciones masivas
            if st.button(" Enviar Recordatorios Masivos"):
                st.info("Sistema de notificaciones masivas en desarrollo")
                # Aquí se integraría la función enviar_notificaciones()
                st.success(" Simulación: Notificaciones masivas programadas")
        
        else:
            st.success(" No hay vencimientos próximos para notificar")
    else:
        st.warning("No se pudieron obtener los vencimientos próximos")
    
    st.subheader(" Enviar Notificación Individual")
    df_socios = obtener_todos_socios()
    if not df_socios.empty:
        socio_seleccionado = st.selectbox(
            "Selecciona un socio",
            options=[f"{s['id']} - {s['nombre']}" for s in df_socios.to_dict('records')]
        )
        
        if st.button(" Enviar Recordatorio Individual"):
            socio_id = socio_seleccionado.split(" - ")[0]
            resultado = enviar_notificacion_individual(socio_id)
            if 'error' not in resultado:
                st.success(f" Notificación enviada a {socio_seleccionado}")
                st.json(resultado)
            else:
                st.error(f" {resultado['error']}")
    else:
        st.warning("No hay socios disponibles para enviar notificaciones")

# Footer
st.markdown("---")
st.markdown("Sistema de Gestión Gimnasio v2.1 |  Con Sistema de Pagos y Notificaciones Integrados")
