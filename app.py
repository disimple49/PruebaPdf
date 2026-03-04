import streamlit as st
import pandas as pd
from fpdf import FPDF
import pdfplumber
import io
import re

st.set_page_config(page_title="Editor de Gastos", page_icon="💰")

def limpiar_monto(valor):
    if not valor: return 0.0
    # Elimina todo lo que no sea número o punto decimal
    limpio = re.sub(r'[^\d.]', '', str(valor).replace(',', '.'))
    try:
        return float(limpio)
    except:
        return 0.0

def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    # Título principal
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Detalle Gastos", border=1, ln=True, align='C')
    pdf.ln(5)
    
    # Texto descriptivo
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(190, 10, "A continuación se van a detallar los diferentes gastos que se van a tener en este mes que son los siguientes.", border=1, align='L')
    pdf.ln(5)
    
    # Tabla
    pdf.set_draw_color(100, 150, 200)
    total = 0
    for i, row in df.iterrows():
        desc = str(row['Descripción'])
        monto = row['Monto']
        total += monto
        
        pdf.cell(15, 10, f"{i+1}._", border='LTB', align='C')
        pdf.cell(140, 10, desc, border='TB', align='L')
        pdf.cell(35, 10, f"${monto:,.2f}", border='RTB', align='R', ln=True)
        
    # Fila de Total
    pdf.set_font("Arial", "B", 12)
    pdf.cell(155, 10, "Total:", border='LTB', align='R')
    pdf.cell(35, 10, f"${total:,.2f}", border=1, align='R', ln=True)
    
    return bytes(pdf.output())

st.title("📊 Gestor de Informes de Gastos")

uploaded_file = st.file_uploader("Sube tu PDF para editar o agregar gastos", type="pdf")

# Inicializar tabla vacía
if "df_gastos" not in st.session_state:
    st.session_state.df_gastos = pd.DataFrame(columns=["Descripción", "Monto"])

# Procesar carga de PDF
if uploaded_file and st.button("Cargar datos del PDF"):
    with pdfplumber.open(uploaded_file) as pdf:
        table = pdf.pages[0].extract_table()
        if table:
            nuevos_datos = []
            for fila in table:
                # Filtrar filas que no sean el total ni estén vacías
                if fila[1] and "Total" not in str(fila[1]):
                    desc = fila[1].replace('\n', ' ')
                    monto = limpiar_monto(fila[2])
                    nuevos_datos.append({"Descripción": desc, "Monto": monto})
            st.session_state.df_gastos = pd.DataFrame(nuevos_datos)
            st.rerun()

# Editor interactivo
st.subheader("📝 Lista de Gastos")
edited_df = st.data_editor(
    st.session_state.df_gastos,
    num_rows="dynamic",
    use_container_width=True,
    column_config={"Monto": st.column_config.NumberColumn(format="$ %.2f")}
)

# Botón para descargar
if not edited_df.empty:
    if st.button("🚀 Crear PDF Final"):
        pdf_out = generar_pdf(edited_df)
        st.download_button(
            label="📥 Descargar Nuevo Informe",
            data=pdf_out,
            file_name="Detalle_Gastos_Nuevo.pdf",
            mime="application/pdf"
        )
