import streamlit as st
import pandas as pd
import math

st.set_page_config(layout="wide", page_title="Diseño de Voladura")

st.title("Diseño de Perforación y Voladura de Rocas")
st.markdown("**(Método Empírico)** - *Explosivo a utilizar: Dinamita Semigelatinosa | Ø Taladro: 38mm*")

# --- 1. PANEL LATERAL (INPUTS) ---
st.sidebar.header("Parámetros de la Labor")
b = st.sidebar.number_input("Base (b) en m", value=3.0, step=0.1)
h = st.sidebar.number_input("Altura (h) en m", value=3.0, step=0.1)
eficiencia = st.sidebar.number_input("Eficiencia de avance (%)", value=85.0, step=1.0)
tipo_roca = st.sidebar.selectbox("Seleccione el Tipo de Roca", ["Dura", "Semidura", "Blanda"])

# --- 2. LÓGICA Y CONSTANTES ---
r = b / 2
S = ((math.pi * (r**2)) / 2) + ((h / 2) * b)
P = (math.pi * r) + h + b
L = math.sqrt(S) / 1.5

if tipo_roca == "Dura":
    E = 0.5
    K = 2.0
    if S < 5.0:
        carga_teorica = 2.75 
    elif S < 10.0:
        carga_teorica = 2.25 
    elif S < 20.0:
        carga_teorica = 1.85 
    else:
        carga_teorica = 1.55 

elif tipo_roca == "Semidura":
    E = 0.6
    K = 1.5
    if S < 5.0:
        carga_teorica = 2.00 
    elif S < 10.0:
        carga_teorica = 1.60 
    elif S < 20.0:
        carga_teorica = 1.20 
    else:
        carga_teorica = 0.90 

else: # Roca Blanda
    E = 0.7
    K = 1.0
    if S < 5.0:
        carga_teorica = 1.25 
    elif S < 10.0:
        carga_teorica = 0.90 
    elif S < 20.0:
        carga_teorica = 0.65 
    else:
        carga_teorica = 0.45 

# Motor de Cálculos Restantes
Av = L * (eficiencia / 100)
Vt = S * L
Vr = S * Av # Volumen de roca

N_teorico = (P / E) + (K * S)
N = round(N_teorico)

metros_perforados = N * L
carga_total = Vr * carga_teorica 

carga_promedio = carga_total / N if N > 0 else 0

kg_m_avance = carga_total / Av
m_perf_m3_derribado = metros_perforados / Vr
factor_potencia = carga_total / Vr

# --- 3. CREACIÓN DE PESTAÑAS ---
tab1, tab2 = st.tabs(["📝 Teoría y Criterios", "🧮 Cálculos y Distribución de Carga"])

with tab1:
    st.header("Criterios de Evaluación y Fórmulas")
    st.write("El diseño se basa en el método empírico, donde los factores dependen de la competencia de la roca y la sección de la labor.")
    
    col_top1, col_top2 = st.columns(2)
    with col_top1:
        st.subheader("Geometría de la Labor")
        st.write("Se calcula el Área ($S$) y Perímetro ($P$) asumiendo un radio $r = base / 2$:")
        st.latex(r"S = \frac{\pi \cdot r^2}{2} + \frac{h}{2} \cdot b")
        st.latex(r"P = \pi \cdot r + h + b")
        
    with col_top2:
        st.subheader("Longitud y Volumen")
        st.write("La longitud de taladro ($L$) se determina por la sección:")
        st.latex(r"L = \frac{\sqrt{S}}{1.5}")
        st.write("El volumen de roca a remover ($V_r$) se calcula como:")
        st.latex(r"V_r = S \cdot L \cdot \left(\frac{Eficiencia}{100}\right)")
        
    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("1. Número de Taladros (N)")
        st.latex(r"N = \frac{P}{E} + K \cdot S")
        st.markdown("""
        **Valores empíricos por tipo de roca:**
        
        | Tipo de Roca | E (Distancia m/tal) | K (Coeficiente tal/m²) |
        | :--- | :--- | :--- |
        | **Dura** | 0.5 | 2.0 |
        | **Semidura** | 0.6 | 1.5 |
        | **Blanda** | 0.7 | 1.0 |
        """)
        
    with col_b:
        st.subheader("2. Criterios de Carga (Dinamita)")
        st.write("El programa evalúa la sección calculada ($S$) y el tipo de roca para asignar el factor de carga adecuado:")
        st.markdown("""
        | Tipo de Roca | S: 1.0 a 5.0 | S: 5.0 a 10.0 | S: 10.0 a 20.0 | S: 20.0 a 40.0 |
        | :--- | :--- | :--- | :--- | :--- |
        | **Dura** | 3.0 a 2.5 | 2.5 a 2.0 | 2.0 a 1.7 | 1.7 a 1.4 |
        | **Semidura** | 2.2 a 1.8 | 1.8 a 1.4 | 1.4 a 1.0 | 1.0 a 0.8 |
        | **Blanda** | 1.5 a 1.0 | 1.0 a 0.8 | 0.8 a 0.5 | 0.5 a 0.4 |
        """)
        
    st.divider()
    st.subheader("3. Distribución Espacial de Taladros")
    st.write("El programa calcula dinámicamente la cantidad de taladros aplicando los siguientes espaciamientos matemáticos a la geometría:")
    st.markdown("""
    * **Arranques:** Valor fijo empírico de **4 taladros** (Corte quemado).
    * **Arrastres:** `Base / 0.6m` (Espaciamiento lineal en el piso).
    * **Cuadradores:** `(Altura de pared recta / 0.6m) * 2 hastiales`.
    * **Corona:** `Perímetro del arco / 0.5m` (Menor espaciamiento por seguridad del techo).
    * **Ayudas:** Se calcula por diferencia `N - (Resto de taladros)` para rellenar la malla.
    """)

with tab2:
    st.header(f"Resultados del Modelo (Roca {tipo_roca})")
    
    st.subheader("Secuencia de Cálculos y Resultados")
    
    col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
    col_c1.metric("1. Sección (S)", f"{round(S, 2)} m²")
    col_c2.metric("2. Perímetro (P)", f"{round(P, 2)} m")
    col_c3.metric("3. Longitud (L)", f"{round(L, 2)} m")
    col_c4.metric("4. Avance Real (Av)", f"{round(Av, 2)} m")
    col_c5.metric("5. Volumen (Vr)", f"{round(Vr, 2)} m³")
    
    st.divider()
    
    col_c6, col_c7, col_c8, col_c9 = st.columns(4)
    col_c6.metric("6. Factor Carga Aplicado", f"{carga_teorica} kg/m³")
    col_c7.metric("7. Carga Total Estimada", f"{round(carga_total, 2)} Kg")
    col_c8.metric("8. Número de Taladros", f"{N} taladros")
    col_c9.metric("9. Kg / Taladro", f"{round(carga_promedio, 2)} Kg")
    
    st.divider()
    
    st.subheader("Distribución de Carga y Secuencia de Disparos")
    
    t_arranques = 4
    t_arrastres = round(b / 0.6)
    t_cuadradores = round((h / 2) / 0.6) * 2
    t_corona = round((math.pi * r) / 0.5)
    t_ayudas = N - (t_arranques + t_arrastres + t_cuadradores + t_corona)
    
    if t_ayudas < 0:
        t_ayudas = 0
        t_corona = N - (t_arranques + t_arrastres + t_cuadradores)
    
    c_arranques = carga_promedio * 1.6
    c_ayudas = carga_promedio * 1.3
    c_arrastres = carga_promedio * 1.0
    c_cuadradores = carga_promedio * 0.7
    c_corona = carga_promedio * 0.4 
    
    val_prom = round(carga_promedio, 2)
    
    datos_tabla = {
        "Secuencia": ["Disparo N°1", "Disparo N°2", "Disparo N°3", "Disparo N°4", "Disparo N°5", "TOTALES"],
        "Nombre Taladros": ["Arranques", "Ayudas", "Arrastres", "Cuadradores", "Corona", ""],
        "Factor de Carga": [f"1.6 x {val_prom}", f"1.3 x {val_prom}", f"1.0 x {val_prom}", f"0.7 x {val_prom}", f"0.4 x {val_prom}", "-"],
        "Kg / Taladro": [round(c_arranques, 2), round(c_ayudas, 2), round(c_arrastres, 2), round(c_cuadradores, 2), round(c_corona, 2), "-"],
        "Cantidad (N)": [t_arranques, t_ayudas, t_arrastres, t_cuadradores, t_corona, N],
        "Total Kg": [round(c_arranques*t_arranques, 2), round(c_ayudas*t_ayudas, 2), round(c_arrastres*t_arrastres, 2), round(c_cuadradores*t_cuadradores, 2), round(c_corona*t_corona, 2), round(carga_total, 2)]
    }
    
    df_distribucion = pd.DataFrame(datos_tabla)
    st.dataframe(df_distribucion, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # --- MODIFICACIÓN: FÓRMULAS AÑADIDAS AQUÍ ---
    st.subheader("Parámetros de Eficiencia")
    st.write("Resultados obtenidos con su respectiva fórmula aplicada:")
    
    st.markdown(f"- **Kg de explosivo / metro de avance:** {round(kg_m_avance, 2)} Kg/m &nbsp;&nbsp;&nbsp;&nbsp; $\\rightarrow \\quad \\frac{{\\text{{Carga Total (Kg)}}}}{{\\text{{Avance Real (Av)}}}}$")
    st.markdown(f"- **Metros perforados / m³ derribado:** {round(m_perf_m3_derribado, 2)} m/m³ &nbsp;&nbsp;&nbsp;&nbsp; $\\rightarrow \\quad \\frac{{N \\cdot L}}{{V_r}}$")
    st.markdown(f"- **Factor de Potencia Real:** {round(factor_potencia, 2)} Kg/m³ &nbsp;&nbsp;&nbsp;&nbsp; $\\rightarrow \\quad \\frac{{\\text{{Carga Total (Kg)}}}}{{V_r}}$")









