import streamlit as st
import pandas as pd
from fpdf import FPDF
import pdfplumber
import io

# Configuración de página
st.set_page_config(page_title="Editor de Gastos", page_icon="💰")

def generar_pdf(df, total):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Título Principal
    pdf.cell(190, 10, "Detalle Gastos", border=1, ln=True, align='C')
    pdf.ln(5)
    
    # Cuadro de texto descriptivo
    pdf.set_font("Arial", "", 11)
    texto_intro = "A continuación se van a detallar los diferentes gastos que se van a tener en este mes que son los siguientes."
    pdf.multi_cell(190, 10, texto_intro, border=1, align='L')
    pdf.ln(5)
    
    # Configuración de la Tabla (Colores y Estilos)
    pdf.set_draw_color(100, 150, 200) # Azul claro como en tu imagen
    pdf.set_line_width(0.3)
    
    for i, row in df.iterrows():
        # Columna de número
        pdf.cell(15, 10, f"{i+1}._ ", border='LTB', align='C')
        # Columna de descripción
        pdf.cell(140, 10, str(row['Descripción']), border='TB', align='L')
        # Columna de monto
        pdf.cell(35, 10, f"${row['Monto']:.2f}", border='RTB', align='R', ln=True)
        
    # Fila de Total
    pdf.set_font("Arial", "B", 12)
    pdf.cell(155, 10, "Total: ", border='LTB', align='R')
    pdf.cell(35, 10, f"${total:.2f}", border=1, align='R', ln=True)
    
    return pdf.output()

st.title("🔧 Editor de Informes de Gastos")

# Opción 1: Cargar PDF anterior
uploaded_file = st.file_uploader("Subir PDF anterior para editar", type="pdf")

# Inicializar o cargar datos
if "df_gastos" not in st.session_state:
    # Datos por defecto si no hay carga
    st.session_state.df_gastos = pd.DataFrame([
        {"Descripción": "Banco Pichincha a nombre de...", "Monto": 0.0}
    ])

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        table = pdf.pages[0].extract_table()
        if table:
            # Limpiar datos extraídos (quitando símbolos de $ y vacíos)
            data = []
            for row in table:
                if row[1] and row[2]: # Si hay descripción y monto
                    desc = row[1]
                    monto = float(row[2].replace('$', '').replace(',', ''))
                    data.append({"Descripción": desc, "Monto": monto})
            st.session_state.df_gastos = pd.DataFrame(data)

# Interfaz de edición
st.subheader("📝 Modifica o agrega gastos abajo:")
edited_df = st.data_editor(
    st.session_state.df_gastos,
    num_rows="dynamic", # Permite agregar y borrar filas
    use_container_width=True,
    column_config={
        "Monto": st.column_config.NumberColumn(format="$ %.2f")
    }
)

# Cálculo de Total en tiempo real
total_actual = edited_df["Monto"].sum()
st.info(f"**Total calculado:** ${total_actual:,.2f}")

# Generar nuevo PDF
if st.button("🚀 Generar Nuevo PDF"):
    pdf_bytes = generar_pdf(edited_df, total_actual)
    st.download_button(
        label="📥 Descargar Informe Actualizado",
        data=pdf_bytes,
        file_name="Detalle_Gastos_Actualizado.pdf",
        mime="application/pdf"
    )
