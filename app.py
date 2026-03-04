import streamlit as st
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt

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
    carga_teorica = 2.25 if S < 10.0 else 1.85 
elif tipo_roca == "Semidura":
    E = 0.6
    K = 1.5
    carga_teorica = 1.60 if S < 10.0 else 1.20 
else: 
    E = 0.7
    K = 1.0
    carga_teorica = 0.90 if S < 10.0 else 0.65 

# Motor de Cálculos Restantes
Av = L * (eficiencia / 100)
Vt = S * L
Vr = S * Av 

N_teorico = (P / E) + (K * S)
N = round(N_teorico)

metros_perforados = N * L
carga_total = Vr * carga_teorica 
carga_promedio = carga_total / N if N > 0 else 0

kg_m_avance = carga_total / Av
m_perf_m3_derribado = metros_perforados / Vr
factor_potencia = carga_total / Vr

# --- LÓGICA DE DISTRIBUCIÓN PARAMÉTRICA ---
t_arranques = 4  
t_arrastres = round(b / 0.6)
t_cuadradores = round((h / 2) / 0.6) * 2
t_corona = round((math.pi * r) / 0.5)
t_ayudas = N - (t_arranques + t_arrastres + t_cuadradores + t_corona)

if t_ayudas < 0:
    t_ayudas = 0
    t_corona = N - (t_arranques + t_arrastres + t_cuadradores)

# --- 3. CREACIÓN DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📝 Teoría y Criterios", "🧮 Cálculos y Distribución", "🎯 Malla Visual"])

with tab1:
    st.header("Criterios de Evaluación y Fórmulas")
    st.write("El diseño se basa en el método empírico, donde los factores dependen de la competencia de la roca y la sección de la labor. Se busca optimizar la cantidad de explosivo y asegurar el avance programado.")
    
    col_top1, col_top2 = st.columns(2)
    with col_top1:
        st.subheader("Geometría de la Labor")
        st.write("Se calcula el Área ($S$) y Perímetro ($P$) asumiendo un techo en forma de arco de medio punto con radio $r = base/2$:")
        st.latex(r"S = \frac{\pi \cdot r^2}{2} + \frac{h}{2} \cdot b")
        st.latex(r"P = \pi \cdot r + h + b")
        
    with col_top2:
        st.subheader("Longitud y Volumen")
        st.write("La longitud de taladro ($L$) se determina en función directa a la sección de la labor:")
        st.latex(r"L = \frac{\sqrt{S}}{1.5}")
        st.latex(r"V_r = S \cdot L \cdot \left(\frac{Eficiencia}{100}\right)")
        
    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("1. Cálculo del Número de Taladros (N)")
        st.write("Fórmula empírica basada en el perímetro y la sección:")
        st.latex(r"N = \frac{P}{E} + K \cdot S")
        st.markdown("""
        | Tipo de Roca | Dist. entre taladros E (m/tal) | Factor K (tal/m²) |
        | :--- | :--- | :--- |
        | **Dura** | 0.5 | 2.0 |
        | **Semidura** | 0.6 | 1.5 |
        | **Blanda** | 0.7 | 1.0 |
        """)
        
    with col_b:
        st.subheader("2. Criterios de Carga Teórica (Dinamita)")
        st.write("Valores empíricos en $kg/m^3$ según el tamaño de la labor:")
        st.markdown("""
        | Tipo de Roca | Sección: 1.0 a 5.0 | Sección: 5.0 a 10.0 | Sección: 10.0 a 20.0 |
        | :--- | :--- | :--- | :--- |
        | **Dura** | 3.0 a 2.5 | 2.5 a 2.0 | 2.0 a 1.7 |
        | **Semidura** | 2.2 a 1.8 | 1.8 a 1.4 | 1.4 a 1.0 |
        | **Blanda** | 1.5 a 1.0 | 1.0 a 0.8 | 0.8 a 0.5 |
        """)

    st.divider()

    # --- NUEVA SECCIÓN DE TEORÍA DE DISTRIBUCIÓN ---
    st.header("Teoría de Distribución de Taladros")
    st.write("La malla visualizada en este diseño está fundamentada en el método de **Corte Quemado (Burn Cut)** con frentes paralelos. Esta distribución geométrica asegura la creación secuencial de caras libres hacia el centro de la labor.")
    
    st.markdown("""
    * **Taladro de Alivio (Vacío central):** Es el corazón de la malla. Se perfora pero no se carga con explosivo. Su único propósito es proporcionar la primera "cara libre" para que la roca fragmentada por los arranques tenga hacia dónde expandirse.
    * **Arranques (1) y Ayudas (2):** Siguen un patrón de expansión geométrica progresiva alternando formas **(Rombo interior $\\rightarrow$ Cuadrado medio $\\rightarrow$ Rombo exterior)**. Esta secuencia radial simétrica garantiza que la cavidad central se agrande capa por capa sin "soplar" o proyectar la roca excesivamente hacia atrás, optimizando el uso de la energía del explosivo.
    * **Arrastres (3):** Situados en el piso de la labor. Son los últimos en detonar (o penúltimos). Requieren mayor concentración de carga ya que deben vencer la gravedad para levantar y empujar todo el material derribado (muck pile) hacia adelante.
    * **Cuadradores (4):** Perforados a lo largo de los hastiales (paredes). Definen el perfil lateral de la galería y ayudan a mantener la estabilidad de los flancos.
    * **Corona (5):** Perforados en el techo (bóveda). Llevan la menor carga explosiva de toda la malla para implementar el principio de voladura controlada (Smooth Blasting). Esto minimiza la sobre-excavación (overbreak) y previene la caída de rocas, garantizando un techo seguro y estable.
    """)

with tab2:
    st.header(f"Resultados del Modelo (Roca {tipo_roca})")
    
    col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
    col_c1.metric("1. Sección (S)", f"{round(S, 2)} m²")
    col_c2.metric("2. Perímetro (P)", f"{round(P, 2)} m")
    col_c3.metric("3. Longitud (L)", f"{round(L, 2)} m")
    col_c4.metric("4. Avance Real (Av)", f"{round(Av, 2)} m")
    col_c5.metric("5. Volumen (Vr)", f"{round(Vr, 2)} m³")
    
    st.divider()
    
    col_c6, col_c7, col_c8, col_c9 = st.columns(4)
    col_c6.metric("6. Factor Carga", f"{carga_teorica} kg/m³")
    col_c7.metric("7. Carga Total", f"{round(carga_total, 2)} Kg")
    col_c8.metric("8. Taladros", f"{N}")
    col_c9.metric("9. Kg/Taladro", f"{round(carga_promedio, 2)} Kg")
    
    st.divider()
    
    c_arranques = carga_promedio * 1.6
    c_ayudas = carga_promedio * 1.3
    c_arrastres = carga_promedio * 1.0
    c_cuadradores = carga_promedio * 0.7
    c_corona = carga_promedio * 0.4 
    
    val_prom = round(carga_promedio, 2)
    
    datos_tabla = {
        "Secuencia": ["Disparo N°1", "Disparo N°2", "Disparo N°3", "Disparo N°4", "Disparo N°5", "TOTALES"],
        "Nombre Taladros": ["Arranques", "Ayudas", "Arrastres", "Cuadradores", "Corona", ""],
        "Factor Carga": [f"1.6 x {val_prom}", f"1.3 x {val_prom}", f"1.0 x {val_prom}", f"0.7 x {val_prom}", f"0.4 x {val_prom}", "-"],
        "Kg/Taladro": [round(c_arranques, 2), round(c_ayudas, 2), round(c_arrastres, 2), round(c_cuadradores, 2), round(c_corona, 2), "-"],
        "Cantidad (N)": [t_arranques, t_ayudas, t_arrastres, t_cuadradores, t_corona, N],
        "Total Kg": [round(c_arranques*t_arranques, 2), round(c_ayudas*t_ayudas, 2), round(c_arrastres*t_arrastres, 2), round(c_cuadradores*t_cuadradores, 2), round(c_corona*t_corona, 2), round(carga_total, 2)]
    }
    
    st.dataframe(pd.DataFrame(datos_tabla), use_container_width=True, hide_index=True)
    st.divider()
    
    st.subheader("Parámetros de Eficiencia")
    st.markdown(f"- **Kg de explosivo / metro de avance:** {round(kg_m_avance, 2)} Kg/m")
    st.markdown(f"- **Metros perforados / m³ derribado:** {round(m_perf_m3_derribado, 2)} m/m³")
    st.markdown(f"- **Factor de Potencia Real:** {round(factor_potencia, 2)} Kg/m³")

with tab3:
    st.header("Visualización de la Malla de Perforación y Secuencia")
    st.write("El plano incluye el corte central tipo diamante/cuadrado con taladro de alivio.")
    
    fig, ax = plt.subplots(figsize=(9, 8))
    
    centro_x, centro_y = b/2, h/2
    altura_total = h/2 + r
    
    # --- DIBUJO DEL TÚNEL Y EJES ---
    pared_izq = np.array([[0, 0], [0, h/2]])
    pared_der = np.array([[b, 0], [b, h/2]])
    piso = np.array([[0, 0], [b, 0]])
    theta_arco = np.linspace(np.pi, 0, 100)
    arco_x = r + r * np.cos(theta_arco)
    arco_y = h/2 + r * np.sin(theta_arco)
    
    ax.plot(pared_izq[:,0], pared_izq[:,1], 'k-', lw=2.5)
    ax.plot(pared_der[:,0], pared_der[:,1], 'k-', lw=2.5)
    ax.plot(piso[:,0], piso[:,1], 'k-', lw=2.5)
    ax.plot(arco_x, arco_y, 'k-', lw=2.5)
    
    # Líneas azules centrales
    ax.plot([0, b], [h/2, h/2], color='dodgerblue', lw=2)
    ax.plot([b/2, b/2], [0, altura_total], color='dodgerblue', lw=2)
    
    # Línea negra de radio
    ax.plot([b/2, b/2 + r*np.cos(np.pi/8)], [h/2, h/2 + r*np.sin(np.pi/8)], color='black', lw=2)
    ax.text(b/2 + (r/2)*np.cos(np.pi/8) - 0.1, h/2 + (r/2)*np.sin(np.pi/8) + 0.15, f"{round(r,2)}m", fontsize=11, rotation=22)
    
    # Cotas rojas externas
    ax.plot([0, b], [-0.3, -0.3], color='red', lw=2)
    ax.text(b/2, -0.5, f"{round(b,2)}m", color='black', fontsize=12, ha='center')
    ax.plot([b+0.3, b+0.3], [0, altura_total], color='red', lw=2)
    ax.text(b+0.4, altura_total/2, f"{round(altura_total,2)}m", color='black', fontsize=12, va='center')

    # --- FUNCIÓN PARA PINTAR PUNTOS Y LÍNEAS ---
    def plot_taladros(x_coords, y_coords, color, label, numero, connect=False, closed=False):
        if connect and len(x_coords) > 1:
            if closed:
                ax.plot(np.append(x_coords, x_coords[0]), np.append(y_coords, y_coords[0]), color='dimgray', lw=1.2, zorder=1)
            else:
                ax.plot(x_coords, y_coords, color='dimgray', lw=1.2, zorder=1)
                
        # Círculo coloreado grande
        if label:
            ax.scatter(x_coords, y_coords, c=color, label=label, s=250, edgecolors='black', zorder=5)
        else:
            ax.scatter(x_coords, y_coords, c=color, s=250, edgecolors='black', zorder=5)
        
        # Número blanco dentro del círculo
        for x, y in zip(x_coords, y_coords):
            ax.text(x, y, str(numero), color='white', fontsize=10, ha='center', va='center', fontweight='bold', zorder=6)

    # --- NUEVA DISTRIBUCIÓN CENTRAL ---
    
    # 0. Alivio (Taladro central vacío, sin explosivo)
    ax.scatter([centro_x], [centro_y], c='white', edgecolors='black', s=250, zorder=5)

    # 1. Arranques / Primera Ayuda (Rombo interior)
    d1_x, d1_y = 0.12 * b, 0.12 * h
    x_arr = [centro_x, centro_x+d1_x, centro_x, centro_x-d1_x]
    y_arr = [centro_y+d1_y, centro_y, centro_y-d1_y, centro_y]
    plot_taladros(x_arr, y_arr, 'red', 'Arranques (1)', 1, connect=True, closed=True)

    # 2A. Ayudas / Segunda Ayuda (Cuadrado medio)
    d2_x, d2_y = 0.20 * b, 0.20 * h
    x_ayuda2 = [centro_x-d2_x, centro_x+d2_x, centro_x+d2_x, centro_x-d2_x]
    y_ayuda2 = [centro_y+d2_y, centro_y+d2_y, centro_y-d2_y, centro_y-d2_y]
    plot_taladros(x_ayuda2, y_ayuda2, 'orange', 'Ayudas (2)', 2, connect=True, closed=True)

    # 2B. Ayudas / Tercera Ayuda (Rombo exterior)
    d3_x, d3_y = 0.32 * b, 0.32 * h
    x_ayuda3 = [centro_x, centro_x+d3_x, centro_x, centro_x-d3_x]
    y_ayuda3 = [centro_y+d3_y, centro_y, centro_y-d3_y, centro_y]
    plot_taladros(x_ayuda3, y_ayuda3, 'orange', '', 2, connect=True, closed=True)

    # --- CONTORNO EXTERIOR ---
    
    # 3. Arrastres (Línea recta en el piso)
    x_arrast = np.linspace(0.1*b, 0.9*b, t_arrastres)
    y_arrast = [0.08*h] * t_arrastres
    plot_taladros(x_arrast, y_arrast, 'blue', 'Arrastres (3)', 3, connect=True, closed=False)

    # 4. Cuadradores y 5. Corona
    y_cuad = np.linspace(0.2*h, h/2, int(t_cuadradores/2))
    x_cuad_izq = [0.06*b] * len(y_cuad)
    x_cuad_der = [0.94*b] * len(y_cuad)
    
    theta_cor = np.linspace(np.pi, 0, t_corona)
    x_cor = centro_x + (r-0.06*b)*np.cos(theta_cor)
    y_cor = centro_y + (r-0.06*b)*np.sin(theta_cor)
    
    x_contorno = list(x_cuad_izq) + list(x_cor) + list(x_cuad_der)[::-1]
    y_contorno = list(y_cuad) + list(y_cor) + list(y_cuad)[::-1]
    ax.plot(x_contorno, y_contorno, color='dimgray', lw=1.2, zorder=1)

    plot_taladros(x_cuad_izq + x_cuad_der, list(y_cuad) + list(y_cuad), 'green', 'Cuadradores (4)', 4, connect=False)
    plot_taladros(x_cor, y_cor, 'gray', 'Corona (5)', 5, connect=False)

    # Ajustes finales
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Leyenda
    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), title="Secuencia de Salida", 
              frameon=True, shadow=True, title_fontsize='11')
    
    st.pyplot(fig)
