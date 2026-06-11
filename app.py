import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import io

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Registro Gremial",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #F7F8FA; }
    .block-container { padding: 1.5rem 2rem; max-width: 1300px; }

    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1A2C5B 0%, #2E4A9E 100%);
        color: white;
        padding: 1.4rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .app-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
    .app-header p  { margin: 0; font-size: 0.85rem; opacity: 0.75; }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 10px;
        padding: 1.1rem 1.4rem;
        box-shadow: 0 1px 4px rgba(0,0,0,.08);
        border-left: 4px solid #2E4A9E;
        margin-bottom: .5rem;
    }
    .kpi-card.warning { border-left-color: #E8A020; }
    .kpi-card.danger  { border-left-color: #C0392B; }
    .kpi-card.ok      { border-left-color: #27AE60; }
    .kpi-label { font-size: .75rem; color: #666; text-transform: uppercase; letter-spacing: .05em; }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #1A2C5B; line-height: 1.1; }

    /* Section titles */
    .section-title {
        font-size: 1rem; font-weight: 600; color: #1A2C5B;
        border-bottom: 2px solid #2E4A9E;
        padding-bottom: .3rem; margin-bottom: 1rem;
    }

    /* Badges de estado */
    .badge-ok      { background:#D5F0E0; color:#1E7E45; padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
    .badge-warn    { background:#FEF0D5; color:#A06010; padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
    .badge-danger  { background:#FCE4E4; color:#A02020; padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }

    /* Form card */
    .form-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,.08);
    }
    div[data-testid="stForm"] { background: white; border-radius: 10px; padding: 1rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background: #1A2C5B; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] .stRadio label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Listas de opciones (según el Excel) ──────────────────────────────────────
MOVILIDAD_OPTS = [
    "Cumple", "No Cumple", "Excede -5min", "Excede 5/10 min",
    "Excede + 10/20min", "Supera + 1/2hs", "SUPERA SEMANA COMPLETA",
    "GENERA PDL", "No realiza actividad gremial", "Cambia de turno",
]
MOTIVO_EXCEDENCIA_OPTS = [
    "NO APLICA", "ASAMBLEA", "SIN INFORMACION", "REUNION JT/GL/GERENCIA",
    "REUNION LABORALES", "REUNION TM/TL", "AUSENTISMO LINEA",
    "REUNION CIR", "Reunion por problemas operativos",
]
LICENCIAS_OPTS = [
    "", "ENFERMEDAD INCULPABLE", "ART", "JUDICIALIDAD", "PERMISO SECTOR",
    "LLEGADA TARDE", "LLT CHARLA DE 5", "SALIDA TEMPRAN SIN MOTIVO",
    "SALIDA TEMPRAN CON MOTIVO", "PARO/MOVILIZACIÓN", "VACACIONES",
    "FALLECIMIENTO FAMILIAR", "CAMBIA DE TURNO", "Paternidad/Maternidad",
]
LLT_OPTS = [
    "", "LLT CON AVISO", "LLT SIN AVISO", "AUSENCIA INJ",
    "AUSENCIA JUSTI", "LLT CHARLA DE 5", "SALIDA TEMPRANA", "AVISO FUERA DE HORA",
]
ACCION_OPTS = [
    "", "Llamado de atención (GL/JT)", "Charla RRLL", "NOTA DESVIO",
    "AP ESCRITO / SUSP", "JUSTIFICADO", "DESCUENTO",
    "EN INVESTIGACIÓN", "PEDIENTE RESOLUCIÓN", "CERRADO",
]
TURNO_OPTS = ["PLANO", "MAÑANA", "TARDE", "NOCHE"]
SECTORES_OPTS = [
    "Ensamble Final División", "Carrocería", "Pintura", "Motores",
    "Logística", "Calidad", "Mantenimiento", "RRHH", "Otro",
]

# ── Persistencia en CSV ───────────────────────────────────────────────────────
DATA_FILE = "registro_gremial.csv"
COLUMNS = [
    "Legajo", "Nombre y Apellido", "Cuerpo Gremial", "Sector", "Cargo",
    "Turno", "Reporta a", "Fecha",
    "Movilidad Gremial x Semana x Dia", "Motivo Excedencia",
    "Licencia", "Informacion Licencia",
    "LLT/Ausencia Inj", "Observaciones Extras",
    "Motivo (Detallar desvios)", "Accion",
]

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype=str)
        # asegurar columnas
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div style="font-size:2.2rem">🏭</div>
  <div>
    <h1>Registro de Bloque Gremial</h1>
    <p>Control de movilidad gremial · 2 horas por turno</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Navegación")
    pagina = st.radio(
        "", ["➕ Cargar Registro", "📊 Reportes", "📁 Ver / Editar Datos", "⬇️ Exportar Excel"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    df_all = load_data()
    st.markdown(f"**Total registros:** {len(df_all)}")
    if not df_all.empty and "Fecha" in df_all.columns:
        try:
            ult = pd.to_datetime(df_all["Fecha"], dayfirst=True).max().strftime("%d/%m/%Y")
            st.markdown(f"**Última carga:** {ult}")
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — CARGAR REGISTRO
# ═══════════════════════════════════════════════════════════════════════════════
if pagina == "➕ Cargar Registro":
    st.markdown('<div class="section-title">Nuevo Registro Diario</div>', unsafe_allow_html=True)

    with st.form("form_carga", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            legajo = st.text_input("Legajo *", placeholder="7323")
            nombre = st.text_input("Nombre y Apellido *", placeholder="Daniel Coronel")
            cuerpo = st.text_input("Cuerpo Gremial", placeholder="ENSAMBLE-MOTORES")
        with c2:
            sector = st.selectbox("Sector", SECTORES_OPTS)
            cargo  = st.text_input("Cargo", placeholder="Delegado")
            turno  = st.selectbox("Turno", TURNO_OPTS)
        with c3:
            reporta = st.text_input("Reporta a", placeholder="Nombre del jefe")
            fecha   = st.date_input("Fecha *", value=date.today(), format="DD/MM/YYYY")

        st.markdown("---")
        st.markdown("**📍 Movilidad y Excedencia**")
        mc1, mc2 = st.columns(2)
        with mc1:
            movilidad = st.selectbox("Movilidad Gremial x Semana x Día *", MOVILIDAD_OPTS)
        with mc2:
            motivo_exc = st.selectbox("Motivo Excedencia", MOTIVO_EXCEDENCIA_OPTS)

        st.markdown("**📋 Licencias / Ausencias**")
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            licencia = st.selectbox("Licencia", LICENCIAS_OPTS)
        with lc2:
            info_lic = st.text_input("Información Licencia")
        with lc3:
            llt = st.selectbox("LLT / Ausencia Inj.", LLT_OPTS)

        st.markdown("**💬 Observaciones y Acción**")
        oc1, oc2, oc3 = st.columns(3)
        with oc1:
            obs_extra = st.text_area("Observaciones Extras", height=80)
        with oc2:
            motivo_desv = st.text_area("Motivo (Detallar desvíos)", height=80)
        with oc3:
            accion = st.selectbox("Acción", ACCION_OPTS)

        submitted = st.form_submit_button("💾 Guardar Registro", use_container_width=True, type="primary")

    if submitted:
        if not legajo or not nombre:
            st.error("⚠️ Completá al menos Legajo y Nombre.")
        else:
            nuevo = {
                "Legajo": legajo.strip(),
                "Nombre y Apellido": nombre.strip(),
                "Cuerpo Gremial": cuerpo,
                "Sector": sector,
                "Cargo": cargo,
                "Turno": turno,
                "Reporta a": reporta,
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Movilidad Gremial x Semana x Dia": movilidad,
                "Motivo Excedencia": motivo_exc,
                "Licencia": licencia,
                "Informacion Licencia": info_lic,
                "LLT/Ausencia Inj": llt,
                "Observaciones Extras": obs_extra,
                "Motivo (Detallar desvios)": motivo_desv,
                "Accion": accion,
            }
            df_all = load_data()
            df_all = pd.concat([df_all, pd.DataFrame([nuevo])], ignore_index=True)
            save_data(df_all)

            # Alerta de cumplimiento
            if movilidad == "Cumple":
                st.success(f"✅ Registro guardado — **{nombre}** cumplió las 2hs gremiales.")
            elif movilidad == "No Cumple":
                st.warning(f"⚠️ Registro guardado — **{nombre}** NO cumplió las 2hs gremiales.")
            elif movilidad in ["No realiza actividad gremial"]:
                st.info(f"ℹ️ Registro guardado — {nombre}: sin actividad gremial.")
            else:
                st.error(f"🚨 Registro guardado — **{nombre}**: {movilidad} (excedencia detectada).")


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — REPORTES
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "📊 Reportes":
    df_all = load_data()
    st.markdown('<div class="section-title">Reportes y Resúmenes</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("Aún no hay registros cargados.")
    else:
        # Parsear fechas
        df_all["_fecha"] = pd.to_datetime(df_all["Fecha"], dayfirst=True, errors="coerce")

        # Filtros
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            delegados = ["Todos"] + sorted(df_all["Nombre y Apellido"].dropna().unique().tolist())
            sel_del = st.selectbox("Filtrar por Delegado", delegados)
        with fc2:
            f_desde = st.date_input("Desde", value=df_all["_fecha"].min().date() if df_all["_fecha"].notna().any() else date.today(), format="DD/MM/YYYY")
        with fc3:
            f_hasta = st.date_input("Hasta", value=date.today(), format="DD/MM/YYYY")

        df_f = df_all.copy()
        if sel_del != "Todos":
            df_f = df_f[df_f["Nombre y Apellido"] == sel_del]
        df_f = df_f[(df_f["_fecha"] >= pd.Timestamp(f_desde)) & (df_f["_fecha"] <= pd.Timestamp(f_hasta))]

        # KPIs
        total      = len(df_f)
        cumple     = (df_f["Movilidad Gremial x Semana x Dia"] == "Cumple").sum()
        no_cumple  = (df_f["Movilidad Gremial x Semana x Dia"] == "No Cumple").sum()
        excedencias = df_f["Movilidad Gremial x Semana x Dia"].isin([
            "Excede -5min","Excede 5/10 min","Excede + 10/20min","Supera + 1/2hs","SUPERA SEMANA COMPLETA","GENERA PDL"
        ]).sum()
        pct_ok = round(cumple / total * 100) if total else 0

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total registros</div><div class="kpi-value">{total}</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-card ok"><div class="kpi-label">Cumple 2hs</div><div class="kpi-value">{cumple} <span style="font-size:1rem;color:#27AE60">({pct_ok}%)</span></div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-card danger"><div class="kpi-label">No Cumple</div><div class="kpi-value">{no_cumple}</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Excedencias</div><div class="kpi-value">{excedencias}</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # Resumen por delegado
        st.markdown("**Resumen por Delegado**")
        resumen = df_f.groupby("Nombre y Apellido")["Movilidad Gremial x Semana x Dia"].value_counts().unstack(fill_value=0)
        for col in ["Cumple","No Cumple","Excede -5min","Excede 5/10 min","Excede + 10/20min","Supera + 1/2hs","SUPERA SEMANA COMPLETA","GENERA PDL"]:
            if col not in resumen.columns:
                resumen[col] = 0

        def estado_badge(row):
            cumple_n = row.get("Cumple", 0)
            nocumple = row.get("No Cumple", 0)
            exc = sum(row.get(c, 0) for c in ["Excede -5min","Excede 5/10 min","Excede + 10/20min","Supera + 1/2hs","SUPERA SEMANA COMPLETA","GENERA PDL"])
            total_r = cumple_n + nocumple + exc
            if total_r == 0:
                return "Sin datos"
            pct = round(cumple_n / total_r * 100)
            if pct >= 80:
                return f'<span class="badge-ok">✅ {pct}% OK</span>'
            elif pct >= 50:
                return f'<span class="badge-warn">⚠️ {pct}% OK</span>'
            else:
                return f'<span class="badge-danger">🚨 {pct}% OK</span>'

        resumen["Estado"] = resumen.apply(estado_badge, axis=1)
        cols_show = ["Cumple","No Cumple","GENERA PDL","Estado"]
        cols_show = [c for c in cols_show if c in resumen.columns]

        st.write(resumen[cols_show].to_html(escape=False), unsafe_allow_html=True)

        st.markdown("---")

        # Evolución semanal
        st.markdown("**Evolución Semanal**")
        df_f["Semana"] = df_f["_fecha"].dt.to_period("W").astype(str)
        evo = df_f.groupby(["Semana","Movilidad Gremial x Semana x Dia"]).size().unstack(fill_value=0)
        st.bar_chart(evo[["Cumple","No Cumple"]] if "Cumple" in evo.columns else evo)


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — VER / EDITAR
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "📁 Ver / Editar Datos":
    df_all = load_data()
    st.markdown('<div class="section-title">Tabla de Registros</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("Aún no hay registros cargados.")
    else:
        # Filtro rápido
        fc1, fc2 = st.columns(2)
        with fc1:
            buscar = st.text_input("🔍 Buscar por nombre o legajo", "")
        with fc2:
            fil_mov = st.selectbox("Filtrar por Movilidad", ["Todos"] + MOVILIDAD_OPTS)

        df_show = df_all.copy()
        if buscar:
            mask = (
                df_show["Nombre y Apellido"].str.contains(buscar, case=False, na=False) |
                df_show["Legajo"].str.contains(buscar, case=False, na=False)
            )
            df_show = df_show[mask]
        if fil_mov != "Todos":
            df_show = df_show[df_show["Movilidad Gremial x Semana x Dia"] == fil_mov]

        st.dataframe(
            df_show.reset_index(drop=True),
            use_container_width=True,
            height=500,
        )
        st.caption(f"Mostrando {len(df_show)} de {len(df_all)} registros.")

        st.markdown("---")
        st.markdown("**⚠️ Eliminar último registro**")
        if st.button("🗑️ Eliminar el último registro cargado"):
            df_all = df_all.iloc[:-1]
            save_data(df_all)
            st.success("Último registro eliminado.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 4 — EXPORTAR
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "⬇️ Exportar Excel":
    df_all = load_data()
    st.markdown('<div class="section-title">Exportar a Excel</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("No hay datos para exportar.")
    else:
        fe1, fe2 = st.columns(2)
        with fe1:
            exp_desde = st.date_input("Desde", value=date.today() - timedelta(days=30), format="DD/MM/YYYY")
        with fe2:
            exp_hasta = st.date_input("Hasta", value=date.today(), format="DD/MM/YYYY")

        delegados_exp = ["Todos"] + sorted(df_all["Nombre y Apellido"].dropna().unique().tolist())
        sel_exp = st.selectbox("Delegado", delegados_exp)

        df_exp = df_all.copy()
        df_exp["_fecha"] = pd.to_datetime(df_exp["Fecha"], dayfirst=True, errors="coerce")
        df_exp = df_exp[(df_exp["_fecha"] >= pd.Timestamp(exp_desde)) & (df_exp["_fecha"] <= pd.Timestamp(exp_hasta))]
        if sel_exp != "Todos":
            df_exp = df_exp[df_exp["Nombre y Apellido"] == sel_exp]
        df_exp = df_exp.drop(columns=["_fecha"])

        st.info(f"Se exportarán **{len(df_exp)} registros**.")

        # Generar Excel en memoria
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_exp.to_excel(writer, index=False, sheet_name="Registro Gremial")
            ws = writer.sheets["Registro Gremial"]
            # Ancho de columnas automático
            for col_cells in ws.columns:
                max_len = max((len(str(c.value or "")) for c in col_cells), default=10)
                ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 40)
        buffer.seek(0)

        nombre_archivo = f"registro_gremial_{exp_desde.strftime('%d%m%Y')}_{exp_hasta.strftime('%d%m%Y')}.xlsx"
        st.download_button(
            label="⬇️ Descargar Excel",
            data=buffer,
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )
