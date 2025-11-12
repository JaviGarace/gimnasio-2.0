# app_web.py - Dashboard con manejo de errores mejorado
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

# ========== FUNCIONES PARA OBTENER DATOS (CON MANEJO DE ERRORES MEJORADO) ==========
def obtener_todos_socios():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/socios/")
        if response.status_code == 200:
            datos = response.json()
            # Filtrar datos válidos (eliminar registros con "string")
            datos_validos = [s for s in datos if s.get('id', '') != 'string']
            return pd.DataFrame(datos_validos)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con la API de socios: {e}")
        return pd.DataFrame()

def obtener_clases():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/clases/")
        if response.status_code == 200:
            datos = response.json()
            return pd.DataFrame(datos)
        else:
            st.error(f"Error al obtener clases: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con la API de clases: {e}")
        return pd.DataFrame()

def obtener_reservas():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/reservas/")
        if response.status_code == 200:
            datos = response.json()
            return pd.DataFrame(datos)
        else:
            st.error(f"Error al obtener reservas: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con la API de reservas: {e}")
        return pd.DataFrame()

def obtener_entradas():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/entradas/")
        if response.status_code == 200:
            datos = response.json()
            return pd.DataFrame(datos)
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def obtener_planes():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/planes/")
        if response.status_code == 200:
            datos = response.json()
            return pd.DataFrame(datos)
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def obtener_pagos():
    try:
        response = requests.get("https://gimnasio-2-0-1.onrender.com/pagos/")
        if response.status_code == 200:
            datos = response.json()
            return pd.DataFrame(datos)
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

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
    
    # ========== MÉTRICAS VISUALES ==========
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
        st.error(" Error al obtener las clases - No hay datos disponibles")

elif opcion == "Reservas":
    st.header(" Gestión de Reservas")
    df_reservas = obtener_reservas()
    df_clases = obtener_clases()
    df_socios = obtener_todos_socios()
    
    if not df_reservas.empty:
        # Mostrar reservas con información detallada
        df_reservas_detalle = df_reservas.copy()
        
        # Añadir información de clase y socio (si está disponible)
        if not df_clases.empty:
            clase_map = {row['id']: row['nombre'] for _, row in df_clases.iterrows()}
            df_reservas_detalle['clase_nombre'] = df_reservas_detalle['clase_id'].map(clase_map)
        
        if not df_socios.empty:
            socio_map = {row['id']: row['nombre'] for _, row in df_socios.iterrows()}
            df_reservas_detalle['socio_nombre'] = df_reservas_detalle['socio_id'].map(socio_map)
        
        st.subheader(" Reservas Activas")
        st.dataframe(df_reservas_detalle, use_container_width=True)
        
        # Estadísticas de reservas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Reservas", len(df_reservas))
        with col2:
            st.metric("Reservas Confirmadas", len(df_reservas[df_reservas['estado'] == 'confirmada']))
        with col3:
            if not df_clases.empty:
                capacidad_total = df_clases['capacidad_max'].sum()
                ocupacion = len(df_reservas) / capacidad_total * 100 if capacidad_total > 0 else 0
                st.metric("Ocupación General", f"{ocupacion:.0f}%")
    else:
        st.info("No hay reservas registradas aún")

# Agregar las otras secciones aquí (Gestión de Socios, Pagos, etc.)

# Footer
st.markdown("---")
st.markdown("Sistema de Gestión Gimnasio v2.1 |  Con Sistema de Pagos y Notificaciones Integrados")
