import streamlit as st
import pandas as pd
import math

# Configuración de la página para que sea más ancha
st.set_page_config(layout="wide", page_title="Diseño de Voladura")

st.title("Diseño de Perforación y Voladura de Rocas")
st.markdown("**(Método Empírico)** - *Explosivo a utilizar: Dinamita al 80% | Ø Taladro: 38mm*")

# --- PANEL LATERAL (INPUTS) ---
st.sidebar.header("Parámetros de la Labor")
S = st.sidebar.number_input("Sección (m²)", value=8.03, step=0.1)
P = st.sidebar.number_input("Perímetro (m)", value=10.71, step=0.1)
L = st.sidebar.number_input("Longitud de taladro (m)", value=1.89, step=0.1)
eficiencia = st.sidebar.number_input("Eficiencia de avance (%)", value=85.0, step=1.0)
tipo_roca = st.sidebar.selectbox("Seleccione el Tipo de Roca", ["Dura", "Semidura", "Suave"])

# --- LÓGICA Y CONSTANTES ---
if tipo_roca == "Dura":
    E = 0.5
    K = 2.0
    carga_teorica = 2.0 
elif tipo_roca == "Semidura":
    E = 0.6
    K = 1.5
    carga_teorica = 1.4 
else: 
    E = 0.7
    K = 1.0
    carga_teorica = 0.8 

# Motor de Cálculos
Av = L * (eficiencia / 100)
Vt = S * L
Vr = S * Av

N_teorico = (P / E) + (K * S)
N = round(N_teorico)

metros_perforados = N * L
carga_total = Vr * carga_teorica # Según el volumen real derribado

kg_m_avance = carga_total / Av
m_perf_m3_derribado = metros_perforados / Vr
factor_potencia = carga_total / Vr

# --- CREACIÓN DE PESTAÑAS ---
tab1, tab2 = st.tabs(["📝 Teoría y Criterios", "🧮 Cálculos y Distribución de Carga"])

with tab1:
    st.header("Criterios de Evaluación y Fórmulas")
    st.write("El diseño se basa en el método empírico, donde los factores dependen de la competencia de la roca.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("1. Número de Taladros (N)")
        st.latex(r"N = \frac{P}{E} + K \cdot S")
        st.write("""
        * **P:** Perímetro de la sección (m).
        * **S:** Sección de la labor (m²).
        * **E:** Distancia entre taladros de la sección (m/tal). Para roca dura es 0.5.
        * **K:** Coeficiente de roca (tal/m²). Para roca dura es 2.0.
        """)
        
    with col_b:
        st.subheader("2. Criterios de Carga")
        st.write("La cantidad estimada de movimiento de roca por disparar se calcula con el volumen de la labor.")
        st.latex(r"Carga_{total} = Volumen_{roca} \times Factor_{roca}")
        st.write("""
        Para los taladros de arranque, se carga de 1.3 a 1.6 veces la carga promedio por taladro, disminuyendo progresivamente hacia las ayudas y cuadradores para un corte eficiente.
        """)

with tab2:
    st.header(f"Resultados del Modelo (Roca {tipo_roca})")
    
    # 1. Indicadores principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Número de Taladros (N)", f"{N} taladros")
    col2.metric("Carga Total Estimada", f"{round(carga_total, 2)} Kg")
    col3.metric("Avance Real", f"{round(Av, 2)} m")
    
    st.divider()
    
    # 2. Tabla de Distribución de Carga (Dinámica)
    st.subheader("Distribución de Carga y Secuencia de Disparos")
    
    # Calculamos la carga promedio por taladro
    carga_promedio = carga_total / N
    
    # Cantidad de taladros (Distribución típica basada en 38 taladros)
    # Se ajusta la corona dinámicamente si N cambia
    t_arranques = 4
    t_ayuda1 = 6
    t_ayuda2 = 7
    t_arrastres = 11
    t_corona = N - (t_arranques + t_ayuda1 + t_ayuda2 + t_arrastres)
    
    # Cargas por taladro según los factores de tu hoja
    c_arranques = carga_promedio * 1.6
    c_ayuda1 = carga_promedio * 1.3
    c_ayuda2 = carga_promedio * 1.0
    c_arrastres = carga_promedio * 1.0
    c_corona = carga_promedio * 0.625 # Reducido para cuidar el techo de la labor
    
    # Creamos un DataFrame de Pandas (Tabla)
    datos_tabla = {
        "Secuencia": ["Disparo N°1", "Disparo N°2", "Disparo N°3", "Disparo N°4", "Disparo N°5", "TOTALES"],
        "Nombre Taladros": ["Arranques", "Ayuda 1", "Ayuda 2", "Arrastres Cuadrador", "Corona Cuadrador", ""],
        "Factor de Carga": ["1.6 x Prom", "1.3 x Prom", "1.0 x Prom", "1.0 x Prom", "Reducida", ""],
        "Kg / Taladro": [round(c_arranques, 2), round(c_ayuda1, 2), round(c_ayuda2, 2), round(c_arrastres, 2), round(c_corona, 2), "-"],
        "Cantidad (N)": [t_arranques, t_ayuda1, t_ayuda2, t_arrastres, t_corona, N],
        "Total Kg": [round(c_arranques*t_arranques, 2), round(c_ayuda1*t_ayuda1, 2), round(c_ayuda2*t_ayuda2, 2), round(c_arrastres*t_arrastres, 2), round(c_corona*t_corona, 2), round(carga_total, 2)]
    }
    
    df_distribucion = pd.DataFrame(datos_tabla)
    # Mostramos la tabla en pantalla de forma elegante
    st.dataframe(df_distribucion, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # 3. Parámetros de eficiencia al final
    st.subheader("Parámetros de Eficiencia")
    st.write(f"- **Kg de explosivo / metro de avance:** {round(kg_m_avance, 2)} Kg/m")
    st.write(f"- **Metros perforados / m³ derribado:** {round(m_perf_m3_derribado, 2)} m/m³")
    st.write(f"- **Factor de Potencia:** {round(factor_potencia, 2)} Kg/m³")