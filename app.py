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
    .block-container { padding: 1.5rem 2rem; max-width: 1300px; }

    /* Header siempre azul con texto blanco */
    .app-header {
        background: linear-gradient(135deg, #1A2C5B 0%, #2E4A9E 100%);
        color: white !important;
        padding: 1.4rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .app-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; color: white !important; }
    .app-header p  { margin: 0; font-size: 0.85rem; opacity: 0.75; color: white !important; }

    /* KPI cards — usan color del tema */
    .kpi-card {
        border-radius: 10px;
        padding: 1.1rem 1.4rem;
        border-left: 4px solid #2E4A9E;
        margin-bottom: .5rem;
    }
    .kpi-card.warning { border-left-color: #E8A020; }
    .kpi-card.danger  { border-left-color: #C0392B; }
    .kpi-card.ok      { border-left-color: #27AE60; }
    .kpi-label { font-size: .75rem; text-transform: uppercase; letter-spacing: .05em; opacity: .7; }
    .kpi-value { font-size: 2rem; font-weight: 700; line-height: 1.1; }

    /* Section titles */
    .section-title {
        font-size: 1rem; font-weight: 600;
        border-bottom: 2px solid #2E4A9E;
        padding-bottom: .3rem; margin-bottom: 1rem;
    }

    /* Badges */
    .badge-ok     { background:#D5F0E0; color:#1E7E45; padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
    .badge-warn   { background:#FEF0D5; color:#A06010; padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }
    .badge-danger { background:#FCE4E4; color:#A02020; padding:2px 10px; border-radius:20px; font-size:.8rem; font-weight:600; }

    /* Sidebar azul */
    section[data-testid="stSidebar"] { background: #1A2C5B !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Base de Delegados ────────────────────────────────────────────────────────
DELEGADOS = {
    "7232":  {"nombre": "Daniel Coronel",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "CIR",      "turno": "BLANCO",   "reporta": "Mauro Bringas"},
    "12738": {"nombre": "Nadia Pasaban",               "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "CIR",      "turno": "NARANJA",  "reporta": "Juan Bizzotto"},
    "605097":{"nombre": "Luciana Dominguez",           "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "CIR",      "turno": "BLANCO",   "reporta": "Martin Gentilini"},
    "8266":  {"nombre": "Esteban Vilches",             "cuerpo": "MH",                 "sector": "Motores Division",             "cargo": "CIR",      "turno": "NARANJA",  "reporta": "Carlos Fuentes"},
    "10018": {"nombre": "Lucia Dana Messa",            "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "CIR",      "turno": "AMARILLO", "reporta": "Marcelo Martinez"},
    "7047":  {"nombre": "Walter Gonzalez",             "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "CIR",      "turno": "NARANJA",  "reporta": "Hugo Taborda"},
    "7652":  {"nombre": "Matias Giroldi",              "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "CIR",      "turno": "AMARILLO", "reporta": "Faustino Carrasco"},
    "12538": {"nombre": "Noelia Celeste Benitez",      "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "CIR",      "turno": "BLANCO",   "reporta": "Leonardo Gonzalez"},
    "9500":  {"nombre": "Nicolas Emanuel Said",        "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Chasis Division",     "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Jose Gorosito"},
    "13264": {"nombre": "Micaela Mazzoni",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Andres Galdames"},
    "1772":  {"nombre": "Miguel Guaraz",               "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Cristian Moreno"},
    "6306":  {"nombre": "Guillermo Ojeda",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Fernando Canerhoff"},
    "7888":  {"nombre": "Mariano Brazuna",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Fernando Canerhoff"},
    "8248":  {"nombre": "Jeronimo Blois",              "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Jose Ibanez"},
    "5228":  {"nombre": "Leandro Escudero",            "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Walter Herrero"},
    "3675":  {"nombre": "Gabriel Monzon",              "cuerpo": "MANTENIMIENTO",      "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "ROT2",     "reporta": "Ariel Amarillo"},
    "1446":  {"nombre": "Victor Gomez",                "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Esteban Kroger"},
    "12398": {"nombre": "Lourdes Anabella Escobar",    "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Facundo Bustos"},
    "12422": {"nombre": "Valeria Soledad Gonzalez",    "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Facundo Bustos"},
    "6807":  {"nombre": "Nestor Peralta",              "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Juan Bizzotto"},
    "1802":  {"nombre": "Nestor Bonuccelli",           "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Marcos Furtado"},
    "12338": {"nombre": "Lucrecia Silvana Guanca",     "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Marcos Furtado"},
    "4553":  {"nombre": "Damian Gomez",                "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Marcos Furtado"},
    "9667":  {"nombre": "Maylen Albelo",               "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Maximiliano Ellemberger"},
    "604590":{"nombre": "Aldana Cabello",              "cuerpo": "SOLDADURA",          "sector": "Frame Division",               "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Pablo Lopez"},
    "7001":  {"nombre": "Alexis Alvarez",              "cuerpo": "SOLDADURA",          "sector": "Frame Division",               "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Pablo Lopez"},
    "9565":  {"nombre": "Braian Campodonico",          "cuerpo": "SOLDADURA",          "sector": "Frame Division",               "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Edmundo Lugo"},
    "6713":  {"nombre": "Lucas Montani",               "cuerpo": "SOLDADURA",          "sector": "Frame Division",               "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ignacio Ibar"},
    "4729":  {"nombre": "Gerardo Rebora",              "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Jose Mateo"},
    "6783":  {"nombre": "Arnolfo Acuna Culzoni",       "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Martin Gentilini"},
    "6287":  {"nombre": "Bruno Sanjurjo",              "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Emanuel Pacher"},
    "13400": {"nombre": "Viviana Pura",                "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ramiro Elizaga"},
    "4583":  {"nombre": "Genaro Augurio",              "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Jose Mateo"},
    "8193":  {"nombre": "Martin Malacalza Portillo",   "cuerpo": "ENSAMBLE & MOTORES", "sector": "Motores Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Cesar Cuenca"},
    "1983":  {"nombre": "Diego Cardozo",               "cuerpo": "MH",                 "sector": "Motores Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Carlos Fuentes"},
    "837":   {"nombre": "Pablo Bruchez",               "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Matias Cardenas"},
    "6717":  {"nombre": "Hector Gonzalez",             "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Ariel Rupp"},
    "6825":  {"nombre": "Juan Seery",                  "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Javier Werner"},
    "11878": {"nombre": "Valeria Soledad Villalba",    "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Javier Werner"},
    "8273":  {"nombre": "Matias Rosales",              "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Cesar Bentancur"},
    "1748":  {"nombre": "Ezequiel Marquez",            "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Javier Werner"},
    "573":   {"nombre": "Horacio Gutierrez",           "cuerpo": "MANTENIMIENTO",      "sector": "Pintura Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Nicolas Echeverria"},
    "4394":  {"nombre": "Diego Quintana",              "cuerpo": "SOLDADURA",          "sector": "Press Division",               "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Julian Lopez"},
    "4310":  {"nombre": "Nestor Uran",                 "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Marcelo Martinez"},
    "5740":  {"nombre": "Enrique Schmidt",             "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Ariel Sena"},
    "4934":  {"nombre": "Leonardo Montiel",            "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ariel Sena"},
    "8641":  {"nombre": "Ariel Monzon",                "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Ruben Ragusa"},
    "1645":  {"nombre": "Nicolas Martin",              "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Diego Vargas"},
    "12376": {"nombre": "Yesica Soledad Guereñu",      "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Diego Irasuegui"},
    "1858":  {"nombre": "Daniel Marcell",              "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Matias Medina"},
    "12643": {"nombre": "Sabrina Denis",               "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Carlos Demierre"},
    "7264":  {"nombre": "Jordan Cirigliano",           "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Jose Martinez"},
    "7942":  {"nombre": "Fernando Albornoz",           "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Diego Mendieta"},
    "605098":{"nombre": "Iara Lopez Rinaldi",          "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Leonardo Gonzalez"},
    "6650":  {"nombre": "Pablo Lasansky",              "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Juan Lindner"},
    "7092":  {"nombre": "Juan Roa",                    "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Federico Medina"},
    "9412":  {"nombre": "Lucas Alvarez",               "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Faustino Carrasco"},
    "8235":  {"nombre": "Mariano Figueroa",            "cuerpo": "MANTENIMIENTO",      "sector": "Welding Division",             "cargo": "Delegado", "turno": "ROT4",     "reporta": "Victor Garcia Calderon"},
}

# ── Listas de opciones (según el Excel) ──────────────────────────────────────
MOVILIDAD_OPTS = [
    "No Cumple", "Excede -5min", "Excede 5/10 min",
    "Excede + 10/20min", "Supera + 1/2hs", "SUPERA SEMANA COMPLETA",
    "GENERA PDL", "Cambia de turno",
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
TURNO_OPTS = ["BLANCO", "NARANJA", "AMARILLO", "ROT2", "ROT4"]
SECTORES_OPTS = [
    "Ensamble Chasis Division",
    "Ensamble Final Division",
    "Ensamble TRIM Division",
    "Frame Division",
    "MH Division",
    "Motores Division",
    "Pintura Division",
    "Press Division",
    "QC Division",
    "Servicio al Cliente Division",
    "Welding Division",
    "Otro",
]

# ── Persistencia en CSV ───────────────────────────────────────────────────────
import os, sys

# ── Ruta compartida en Teams/OneDrive ────────────────────────────────────────
TEAMS_PATH = r"C:\users\Eliana.Torres\OneDrive - Toyota Argentina S.A\HR PLANT - Seguimiento gremial 2026"

# Si la carpeta de Teams existe la usamos; si no (otra PC con distinto usuario)
# guardamos en la misma carpeta del ejecutable/script
if os.path.isdir(TEAMS_PATH):
    DATA_FILE = os.path.join(TEAMS_PATH, "registro_gremial.csv")
else:
    # En otras PCs: buscar OneDrive automáticamente
    _base = os.path.expanduser("~")
    _onedrive = None
    for _d in os.listdir(_base):
        _full = os.path.join(_base, _d)
        if "onedrive" in _d.lower() and "toyota" in _d.lower() and os.path.isdir(_full):
            _onedrive = _full
            break
    if _onedrive:
        _teams = os.path.join(_onedrive, "HR PLANT - Seguimiento gremial 2026")
        if os.path.isdir(_teams):
            DATA_FILE = os.path.join(_teams, "registro_gremial.csv")
        else:
            DATA_FILE = os.path.join(_onedrive, "registro_gremial.csv")
    else:
        DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro_gremial.csv")
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
        "", ["➕ Cargar Registro", "📋 Presencia del Día", "📊 Reportes", "📈 Dashboard Gerencial", "📁 Ver / Editar Datos", "⬆️ Importar Histórico", "⬇️ Exportar Excel"],
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

    # Filtro por sector + selector de delegado
    f1, f2 = st.columns(2)
    with f1:
        sector_filtro = st.selectbox("🏭 Filtrar por Sector", ["Todos"] + SECTORES_OPTS, key="filtro_sector")
    with f2:
        if sector_filtro == "Todos":
            delegados_filtrados = sorted(DELEGADOS.items(), key=lambda x: x[1]['nombre'])
        else:
            delegados_filtrados = sorted([(k,v) for k,v in DELEGADOS.items() if v['sector'] == sector_filtro], key=lambda x: x[1]['nombre'])

        nombres_lista = ["— Seleccioná un delegado —"] + [f"{leg} · {d['nombre']}" for leg, d in delegados_filtrados]
        sel = st.selectbox("👤 Seleccioná el delegado", nombres_lista, key="sel_delegado")

    if sel != "— Seleccioná un delegado —":
        leg_auto = sel.split(" · ")[0]
        delegado_data = DELEGADOS.get(leg_auto, {})
    else:
        leg_auto = ""
        delegado_data = {}

    if delegado_data:
        st.success(f"✅ **{delegado_data['nombre']}** — {delegado_data['sector']} | Turno: {delegado_data['turno']}")

    with st.form("form_carga", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            legajo = st.text_input("Legajo *", value=leg_auto)
            nombre = st.text_input("Nombre y Apellido *", value=delegado_data.get("nombre", ""))
            cuerpo = st.text_input("Cuerpo Gremial", value=delegado_data.get("cuerpo", ""))
        with c2:
            sector_val = delegado_data.get("sector", SECTORES_OPTS[0])
            sector_idx = SECTORES_OPTS.index(sector_val) if sector_val in SECTORES_OPTS else 0
            sector = st.selectbox("Sector", SECTORES_OPTS, index=sector_idx)
            cargo  = st.text_input("Cargo", value=delegado_data.get("cargo", ""))
            turno_val = delegado_data.get("turno", TURNO_OPTS[0])
            turno_idx = TURNO_OPTS.index(turno_val) if turno_val in TURNO_OPTS else 0
            turno  = st.selectbox("Turno", TURNO_OPTS, index=turno_idx)
        with c3:
            reporta = st.text_input("Reporta a", value=delegado_data.get("reporta", ""))
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
    st.markdown('<div class="section-title">📊 Reporte Gerencial de Desvíos</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("Aún no hay registros cargados.")
    else:
        df_all["_fecha"] = pd.to_datetime(df_all["Fecha"], dayfirst=True, errors="coerce")
        DESVIOS_REP = ["No Cumple","Excede -5min","Excede 5/10 min","Excede + 10/20min",
                       "Supera + 1/2hs","SUPERA SEMANA COMPLETA","GENERA PDL"]

        # ── Filtros ──
        f1, f2, f3 = st.columns(3)
        with f1:
            sectores_disp = ["Todos"] + sorted(df_all["Sector"].dropna().unique().tolist())
            sel_sector = st.selectbox("Sector", sectores_disp, key="rep_sector")
        with f2:
            df_base_fil = df_all if sel_sector == "Todos" else df_all[df_all["Sector"] == sel_sector]
            delegados_op = ["Todos"] + sorted(df_base_fil["Nombre y Apellido"].dropna().unique().tolist())
            sel_del = st.selectbox("Delegado", delegados_op, key="rep_del")
        with f3:
            jefes_op = ["Todos"] + sorted(df_all["Reporta a"].dropna().unique().tolist())
            sel_jefe = st.selectbox("Reporta a (Jefe)", jefes_op, key="rep_jefe")

        fd1, fd2 = st.columns(2)
        with fd1:
            f_desde = st.date_input("Desde", value=df_all["_fecha"].min().date() if df_all["_fecha"].notna().any() else date.today(), format="DD/MM/YYYY", key="rep_desde")
        with fd2:
            f_hasta = st.date_input("Hasta", value=date.today(), format="DD/MM/YYYY", key="rep_hasta")

        df_f = df_all.copy()
        if sel_sector != "Todos": df_f = df_f[df_f["Sector"] == sel_sector]
        if sel_del   != "Todos": df_f = df_f[df_f["Nombre y Apellido"] == sel_del]
        if sel_jefe  != "Todos": df_f = df_f[df_f["Reporta a"] == sel_jefe]
        df_f = df_f[(df_f["_fecha"] >= pd.Timestamp(f_desde)) & (df_f["_fecha"] <= pd.Timestamp(f_hasta))]
        df_f["_es_desvio"] = df_f["Movilidad Gremial x Semana x Dia"].isin(DESVIOS_REP)

        tot_dev   = df_f["_es_desvio"].sum()
        del_afect = df_f[df_f["_es_desvio"]]["Nombre y Apellido"].nunique()
        reincid_s = df_f[df_f["_es_desvio"]].groupby("Nombre y Apellido").size()
        reincid   = (reincid_s >= 3).sum()
        sector_top = df_f[df_f["_es_desvio"]]["Sector"].value_counts().idxmax() if tot_dev > 0 else "—"

        # ── KPIs ──
        k1,k2,k3,k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Total Desvíos</div><div class="kpi-value">{tot_dev}</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Delegados afectados</div><div class="kpi-value">{del_afect}</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-card {"danger" if reincid>0 else "ok"}"><div class="kpi-label">Reincidentes (≥3 dev.)</div><div class="kpi-value">{reincid}</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Sector más crítico</div><div class="kpi-value" style="font-size:1rem">{sector_top}</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── SECCIÓN 1: RESPONSABILIDAD POR JEFE ──
        st.markdown("### 👔 Responsabilidad por Jefe")
        st.caption("¿Qué jefe tiene más delegados con desvíos? Para reclamar hacia adentro.")

        jefe_total = df_f.groupby("Reporta a").size()
        jefe_dev   = df_f[df_f["_es_desvio"]].groupby("Reporta a").size()
        jefe_df    = pd.DataFrame({"Total": jefe_total, "Desvíos": jefe_dev}).fillna(0).astype(int)
        jefe_df["Tasa %"] = (jefe_df["Desvíos"] / jefe_df["Total"] * 100).round(1)
        jefe_df["Del. con desvíos"] = df_f[df_f["_es_desvio"]].groupby("Reporta a")["Nombre y Apellido"].nunique()
        jefe_df = jefe_df.sort_values("Desvíos", ascending=False)

        for jefe, row in jefe_df.iterrows():
            if not jefe or str(jefe).strip() == "" or str(jefe) == "nan": continue
            tasa_j = row["Tasa %"]
            color_j = "#C0392B" if tasa_j > 20 else "#E67E22" if tasa_j > 10 else "#27AE60"
            # Delegados de este jefe con desvíos
            dels_dev = df_f[(df_f["Reporta a"] == jefe) & df_f["_es_desvio"]]["Nombre y Apellido"].value_counts()
            dels_txt = " · ".join([f"{n} ({c})" for n,c in dels_dev.head(4).items()])
            st.markdown(f"""
            <div style="border-left:4px solid {color_j};padding:10px 16px;margin-bottom:8px;background:#fafafa;border-radius:0 8px 8px 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-weight:700">{jefe}</span>
                        <span style="color:#666;font-size:.8rem;margin-left:8px">{int(row['Del. con desvíos'])} delegados con desvíos</span>
                    </div>
                    <span style="background:{color_j};color:white;padding:3px 10px;border-radius:20px;font-weight:700;font-size:.85rem">{int(row['Desvíos'])} dev. — {tasa_j}%</span>
                </div>
                <div style="color:#888;font-size:.8rem;margin-top:4px">{dels_txt}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── SECCIÓN 2: REINCIDENTES ──
        st.markdown("### 🔁 Reincidentes — 3 o más desvíos en el período")
        st.caption("Los casos prioritarios para escalar o accionar.")

        dev_por_del = df_f[df_f["_es_desvio"]].groupby("Nombre y Apellido").size().sort_values(ascending=False)
        reincidentes = dev_por_del[dev_por_del >= 3]

        if reincidentes.empty:
            st.success("✅ Sin reincidentes en el período.")
        else:
            for nombre, n_dev in reincidentes.items():
                grupo = df_f[(df_f["Nombre y Apellido"] == nombre) & df_f["_es_desvio"]].sort_values("_fecha")
                sector = df_f[df_f["Nombre y Apellido"] == nombre]["Sector"].iloc[0]
                jefe   = df_f[df_f["Nombre y Apellido"] == nombre]["Reporta a"].iloc[0]
                turno  = df_f[df_f["Nombre y Apellido"] == nombre]["Turno"].iloc[0]
                total_d = len(df_f[df_f["Nombre y Apellido"] == nombre])
                pct_d  = round(n_dev / total_d * 100, 1)
                color_r = "#C0392B" if pct_d > 30 else "#E67E22"
                accion_last = df_f[df_f["Nombre y Apellido"] == nombre]["Accion"].dropna().replace("","").last_valid_index()
                accion_txt = df_f.loc[accion_last, "Accion"] if accion_last else "Sin acción registrada"

                fechas_dev = " · ".join(grupo["_fecha"].dt.strftime("%d/%m").tolist())
                tipos = grupo["Movilidad Gremial x Semana x Dia"].value_counts()
                tipos_txt = " / ".join([f"{t}: {c}" for t,c in tipos.items()])

                st.markdown(f"""
                <div style="border:1px solid {color_r};border-radius:8px;padding:14px;margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                        <div>
                            <span style="font-weight:700;font-size:1rem">{nombre}</span><br>
                            <span style="color:#666;font-size:.8rem">{sector} · Turno {turno} · Reporta a: <b>{jefe}</b></span>
                        </div>
                        <span style="background:{color_r};color:white;padding:4px 14px;border-radius:20px;font-weight:700">{n_dev} desvíos — {pct_d}%</span>
                    </div>
                    <div style="font-size:.82rem;color:#444;margin-bottom:4px">📅 Fechas: {fechas_dev}</div>
                    <div style="font-size:.82rem;color:#444;margin-bottom:4px">📋 Tipos: {tipos_txt}</div>
                    <div style="font-size:.82rem;color:#888">⚡ Última acción: {accion_txt}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── SECCIÓN 3: DETALLE COMPLETO ──
        with st.expander("📋 Ver detalle completo de todos los desvíos"):
            df_desvios = df_f[df_f["_es_desvio"]].copy()
            df_desvios["_fecha_fmt"] = df_desvios["_fecha"].dt.strftime("%d/%m/%Y")

            if df_desvios.empty:
                st.success("✅ Sin desvíos en el período.")
            else:
                for nombre, grupo in sorted(df_desvios.groupby("Nombre y Apellido"), key=lambda x: len(x[1]), reverse=True):
                    sector = grupo["Sector"].iloc[0]
                    turno  = grupo["Turno"].iloc[0]
                    n_dev  = len(grupo)
                    total_del = len(df_f[df_f["Nombre y Apellido"] == nombre])
                    pct_dev = round(n_dev / total_del * 100, 1) if total_del else 0
                    color = "#C0392B" if pct_dev > 20 else "#E67E22" if pct_dev > 10 else "#F39C12"

                    detalle_items = []
                    for _, row in grupo.sort_values("_fecha").iterrows():
                        mov    = row["Movilidad Gremial x Semana x Dia"]
                        fecha  = row["_fecha_fmt"]
                        motivo = str(row["Motivo Excedencia"]) if pd.notna(row["Motivo Excedencia"]) and str(row["Motivo Excedencia"]).strip() not in ["","NO APLICA","nan"] else ""
                        llt    = str(row["LLT/Ausencia Inj"]) if pd.notna(row["LLT/Ausencia Inj"]) and str(row["LLT/Ausencia Inj"]).strip() not in ["","nan"] else ""
                        obs    = str(row["Observaciones Extras"]) if pd.notna(row["Observaciones Extras"]) and str(row["Observaciones Extras"]).strip() not in ["","nan"] else ""
                        extra  = " · ".join([x for x in [motivo, llt, obs] if x])
                        detalle_items.append(f"<b>{fecha}</b> — {mov}" + (f" <span style='color:#666'>({extra})</span>" if extra else ""))

                    st.markdown(f"""
                    <div style="border-left:4px solid {color};padding:12px 16px;margin-bottom:10px;background:#fafafa;border-radius:0 8px 8px 0;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <div>
                                <span style="font-weight:700">{nombre}</span>
                                <span style="color:#666;font-size:.85rem;margin-left:10px">{sector} · Turno {turno}</span>
                            </div>
                            <span style="background:{color};color:white;padding:4px 12px;border-radius:20px;font-weight:700;font-size:.85rem">{n_dev} dev. — {pct_dev}%</span>
                        </div>
                        <div style="font-size:.85rem;color:#444;line-height:1.8">{"<br>".join(detalle_items)}</div>
                    </div>""", unsafe_allow_html=True)



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

        df_show_idx = df_show.copy()
        df_show_idx.insert(0, "#", df_all.index[df_all.index.isin(df_show.index)])
        st.dataframe(
            df_show.reset_index(drop=True),
            use_container_width=True,
            height=500,
        )
        st.caption(f"Mostrando {len(df_show)} de {len(df_all)} registros.")

        st.markdown("---")
        st.markdown("**🗑️ Eliminar un registro**")
        ec1, ec2 = st.columns(2)
        with ec1:
            st.markdown("**Eliminar el último registro cargado:**")
            if st.button("🗑️ Eliminar último registro"):
                df_all = df_all.iloc[:-1]
                save_data(df_all)
                st.success("Último registro eliminado.")
                st.rerun()
        with ec2:
            st.markdown("**Eliminar registro específico:**")
            if not df_show.empty:
                indices_disponibles = list(df_show.index)
                fila_a_borrar = st.selectbox(
                    "Seleccioná el registro a eliminar",
                    options=indices_disponibles,
                    format_func=lambda i: f"{df_all.loc[i, 'Nombre y Apellido']} | {df_all.loc[i, 'Fecha']} | {df_all.loc[i, 'Movilidad Gremial x Semana x Dia']}"
                )
                if st.button("🗑️ Eliminar registro seleccionado", type="primary"):
                    df_all = df_all.drop(index=fila_a_borrar).reset_index(drop=True)
                    save_data(df_all)
                    st.success("Registro eliminado correctamente.")
                    st.rerun()

        st.markdown("---")
        st.markdown("**✏️ Editar un registro**")
        if not df_show.empty:
            indices_edit = list(df_show.index)
            fila_edit = st.selectbox(
                "Seleccioná el registro a editar",
                options=indices_edit,
                format_func=lambda i: f"{df_all.loc[i, 'Nombre y Apellido']} | {df_all.loc[i, 'Fecha']} | {df_all.loc[i, 'Movilidad Gremial x Semana x Dia']}",
                key="sel_edit"
            )
            row = df_all.loc[fila_edit]
            with st.form("form_editar"):
                e1, e2, e3 = st.columns(3)
                with e1:
                    e_nombre  = st.text_input("Nombre y Apellido", value=row["Nombre y Apellido"])
                    e_legajo  = st.text_input("Legajo", value=row["Legajo"])
                    e_cuerpo  = st.text_input("Cuerpo Gremial", value=row["Cuerpo Gremial"])
                with e2:
                    e_sector_idx = SECTORES_OPTS.index(row["Sector"]) if row["Sector"] in SECTORES_OPTS else 0
                    e_sector  = st.selectbox("Sector", SECTORES_OPTS, index=e_sector_idx)
                    e_cargo   = st.text_input("Cargo", value=row["Cargo"])
                    e_turno_idx = TURNO_OPTS.index(row["Turno"]) if row["Turno"] in TURNO_OPTS else 0
                    e_turno   = st.selectbox("Turno", TURNO_OPTS, index=e_turno_idx)
                with e3:
                    e_reporta = st.text_input("Reporta a", value=row["Reporta a"])
                    try:
                        e_fecha = st.date_input("Fecha", value=pd.to_datetime(row["Fecha"], dayfirst=True), format="DD/MM/YYYY")
                    except:
                        e_fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

                em1, em2 = st.columns(2)
                with em1:
                    mov_idx = MOVILIDAD_OPTS.index(row["Movilidad Gremial x Semana x Dia"]) if row["Movilidad Gremial x Semana x Dia"] in MOVILIDAD_OPTS else 0
                    e_mov = st.selectbox("Movilidad Gremial", MOVILIDAD_OPTS, index=mov_idx)
                with em2:
                    mot_idx = MOTIVO_EXCEDENCIA_OPTS.index(row["Motivo Excedencia"]) if row["Motivo Excedencia"] in MOTIVO_EXCEDENCIA_OPTS else 0
                    e_motexc = st.selectbox("Motivo Excedencia", MOTIVO_EXCEDENCIA_OPTS, index=mot_idx)

                el1, el2, el3 = st.columns(3)
                with el1:
                    lic_idx = LICENCIAS_OPTS.index(row["Licencia"]) if row["Licencia"] in LICENCIAS_OPTS else 0
                    e_lic = st.selectbox("Licencia", LICENCIAS_OPTS, index=lic_idx)
                with el2:
                    e_infoLic = st.text_input("Info Licencia", value=row["Informacion Licencia"])
                with el3:
                    llt_idx = LLT_OPTS.index(row["LLT/Ausencia Inj"]) if row["LLT/Ausencia Inj"] in LLT_OPTS else 0
                    e_llt = st.selectbox("LLT/Ausencia", LLT_OPTS, index=llt_idx)

                eo1, eo2, eo3 = st.columns(3)
                with eo1:
                    e_obs = st.text_area("Observaciones", value=row["Observaciones Extras"], height=70)
                with eo2:
                    e_motdesv = st.text_area("Motivo Desvío", value=row["Motivo (Detallar desvios)"], height=70)
                with eo3:
                    acc_idx = ACCION_OPTS.index(row["Accion"]) if row["Accion"] in ACCION_OPTS else 0
                    e_acc = st.selectbox("Acción", ACCION_OPTS, index=acc_idx)

                if st.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True):
                    df_all.loc[fila_edit, "Nombre y Apellido"] = e_nombre
                    df_all.loc[fila_edit, "Legajo"] = e_legajo
                    df_all.loc[fila_edit, "Cuerpo Gremial"] = e_cuerpo
                    df_all.loc[fila_edit, "Sector"] = e_sector
                    df_all.loc[fila_edit, "Cargo"] = e_cargo
                    df_all.loc[fila_edit, "Turno"] = e_turno
                    df_all.loc[fila_edit, "Reporta a"] = e_reporta
                    df_all.loc[fila_edit, "Fecha"] = e_fecha.strftime("%d/%m/%Y")
                    df_all.loc[fila_edit, "Movilidad Gremial x Semana x Dia"] = e_mov
                    df_all.loc[fila_edit, "Motivo Excedencia"] = e_motexc
                    df_all.loc[fila_edit, "Licencia"] = e_lic
                    df_all.loc[fila_edit, "Informacion Licencia"] = e_infoLic
                    df_all.loc[fila_edit, "LLT/Ausencia Inj"] = e_llt
                    df_all.loc[fila_edit, "Observaciones Extras"] = e_obs
                    df_all.loc[fila_edit, "Motivo (Detallar desvios)"] = e_motdesv
                    df_all.loc[fila_edit, "Accion"] = e_acc
                    save_data(df_all)
                    st.success("✅ Registro actualizado correctamente.")
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


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 5 — DASHBOARD GERENCIAL
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "📈 Dashboard Gerencial":
    df_all = load_data()

    if df_all.empty:
        st.info("Aún no hay registros cargados.")
    else:
        df_all["_fecha"] = pd.to_datetime(df_all["Fecha"], dayfirst=True, errors="coerce")

        # ── Filtros ──
        fc1, fc2 = st.columns(2)
        with fc1:
            d_desde = st.date_input("Desde", value=date.today() - timedelta(days=180), format="DD/MM/YYYY", key="dash_desde")
        with fc2:
            d_hasta = st.date_input("Hasta", value=date.today(), format="DD/MM/YYYY", key="dash_hasta")

        df_d = df_all[(df_all["_fecha"] >= pd.Timestamp(d_desde)) & (df_all["_fecha"] <= pd.Timestamp(d_hasta))].copy()

        if df_d.empty:
            st.warning("No hay datos en ese período.")
        else:
            DESVIOS = ["No Cumple","Excede -5min","Excede 5/10 min","Excede + 10/20min","Supera + 1/2hs","SUPERA SEMANA COMPLETA","GENERA PDL"]
            LLT_DESVIOS = ["LLT CON AVISO","LLT SIN AVISO","LLT CHARLA DE 5","SALIDA TEMPRANA","AVISO FUERA DE HORA"]

            df_d["es_desvio"]  = df_d["Movilidad Gremial x Semana x Dia"].isin(DESVIOS)
            df_d["es_llt"]     = df_d["LLT/Ausencia Inj"].isin(LLT_DESVIOS)
            df_d["_mes"]       = df_d["_fecha"].dt.to_period("M")
            df_d["_mes_nombre"]= df_d["_fecha"].dt.strftime("%B %Y")

            total      = len(df_d)
            tot_dev    = df_d["es_desvio"].sum()
            del_afect  = df_d[df_d["es_desvio"]]["Nombre y Apellido"].nunique()
            tasa_dev   = round(tot_dev / total * 100, 1) if total else 0

            # ── SECCIÓN 1: INDICADORES CLAVE ──
            st.markdown("""
            <div style="background:#1A2C5B;color:white;padding:12px 20px;border-radius:8px;margin-bottom:16px;">
                <b style="font-size:1.1rem;letter-spacing:.05em">CONTEXTO — INDICADORES CLAVES</b>
            </div>""", unsafe_allow_html=True)

            k1, k2, k3, k4 = st.columns(4)
            periodo_txt = f"{d_desde.strftime('%d/%m/%y')} – {d_hasta.strftime('%d/%m/%y')}"

            # Semana con más desvíos
            dev_x_sem = df_d[df_d["es_desvio"]].groupby(df_d["_fecha"].dt.to_period("W")).size()
            sem_max = dev_x_sem.idxmax() if not dev_x_sem.empty else None
            sem_max_txt = str(sem_max) if sem_max else "—"
            sem_max_val = int(dev_x_sem.max()) if not dev_x_sem.empty else 0

            # Semana con más tasa
            sem_total = df_d.groupby(df_d["_fecha"].dt.to_period("W")).size()
            sem_dev   = df_d[df_d["es_desvio"]].groupby(df_d["_fecha"].dt.to_period("W")).size()
            sem_tasa  = (sem_dev / sem_total * 100).round(1)
            sem_tasa_max = sem_tasa.idxmax() if not sem_tasa.empty else None
            sem_tasa_txt = f"{sem_tasa.max():.1f}%" if not sem_tasa.empty else "—"

            with k1:
                st.markdown(f"""<div style="border:1px solid #ddd;border-radius:8px;padding:16px;text-align:center;">
                    <div style="font-size:.7rem;color:#666;text-transform:uppercase;letter-spacing:.05em">Registros Analizados</div>
                    <div style="font-size:2.2rem;font-weight:700;color:#C0392B">{total:,}</div>
                    <div style="font-size:.75rem;color:#888">{periodo_txt}</div></div>""", unsafe_allow_html=True)
            with k2:
                st.markdown(f"""<div style="border:1px solid #ddd;border-radius:8px;padding:16px;text-align:center;">
                    <div style="font-size:.7rem;color:#666;text-transform:uppercase;letter-spacing:.05em">Total de Desvíos</div>
                    <div style="font-size:2.2rem;font-weight:700;color:#E67E22">{tot_dev:,}</div>
                    <div style="font-size:.75rem;color:#888">Sem. mayor: {sem_max_val} dev.</div></div>""", unsafe_allow_html=True)
            with k3:
                color_tasa = "#C0392B" if tasa_dev > 15 else "#E67E22" if tasa_dev > 10 else "#27AE60"
                st.markdown(f"""<div style="border:1px solid #ddd;border-radius:8px;padding:16px;text-align:center;">
                    <div style="font-size:.7rem;color:#666;text-transform:uppercase;letter-spacing:.05em">Tasa de Desvío</div>
                    <div style="font-size:2.2rem;font-weight:700;color:{color_tasa}">{tasa_dev}%</div>
                    <div style="font-size:.75rem;color:#888">Pico: {sem_tasa_txt}</div></div>""", unsafe_allow_html=True)
            with k4:
                st.markdown(f"""<div style="border:1px solid #ddd;border-radius:8px;padding:16px;text-align:center;">
                    <div style="font-size:.7rem;color:#666;text-transform:uppercase;letter-spacing:.05em">Delegados afectados</div>
                    <div style="font-size:2.2rem;font-weight:700;color:#E67E22">{del_afect:,}</div>
                    <div style="font-size:.75rem;color:#888">con al menos 1 desvío</div></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── SECCIÓN 2: TENDENCIA MENSUAL ──
            st.markdown("""<div style="background:#1A2C5B;color:white;padding:12px 20px;border-radius:8px;margin-bottom:16px;">
                <b style="font-size:1.1rem;letter-spacing:.05em">TENDENCIA MENSUAL DE DESVÍOS</b></div>""", unsafe_allow_html=True)

            mes_total = df_d.groupby("_mes_nombre").size()
            mes_dev   = df_d[df_d["es_desvio"]].groupby("_mes_nombre").size()
            mes_tasa  = (mes_dev / mes_total * 100).round(1)

            # Ordenar meses cronológicamente
            MESES_ES = {"January":"Enero","February":"Febrero","March":"Marzo","April":"Abril",
                        "May":"Mayo","June":"Junio","July":"Julio","August":"Agosto",
                        "September":"Septiembre","October":"Octubre","November":"Noviembre","December":"Diciembre"}
            mes_dev_sorted = mes_dev.copy()
            mes_dev_sorted.index = pd.to_datetime(mes_dev_sorted.index, format="%B %Y", errors="coerce")
            mes_dev_sorted = mes_dev_sorted.sort_index()
            mes_dev_sorted.index = [f"{MESES_ES.get(d.strftime('%B'), d.strftime('%B'))} {d.year}" for d in mes_dev_sorted.index]
            mes_tasa_sorted = mes_tasa.copy()
            mes_tasa_sorted.index = pd.to_datetime(mes_tasa_sorted.index, format="%B %Y", errors="coerce")
            mes_tasa_sorted = mes_tasa_sorted.sort_index()
            mes_tasa_sorted.index = [f"{MESES_ES.get(d.strftime('%B'), d.strftime('%B'))} {d.year}" for d in mes_tasa_sorted.index]

            st.bar_chart(mes_dev_sorted.rename("Desvíos"))
            # Cards de tasa por mes en una fila
            n_meses = len(mes_tasa_sorted)
            if n_meses > 0:
                cols_mes = st.columns(min(n_meses, 6))
                for i, (mes, tasa) in enumerate(mes_tasa_sorted.items()):
                    color = "#C0392B" if tasa > 15 else "#E67E22" if tasa > 10 else "#27AE60"
                    with cols_mes[i % 6]:
                        st.markdown(f"""<div style="text-align:center;padding:8px;border-top:3px solid {color};background:#f9f9f9;border-radius:4px;">
                            <div style="font-size:.75rem;color:#666">{mes}</div>
                            <div style="font-size:1.1rem;font-weight:700;color:{color}">{tasa}%</div>
                        </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── SECCIÓN 3: DESVÍOS POR SECTOR ──
            st.markdown("""<div style="background:#1A2C5B;color:white;padding:12px 20px;border-radius:8px;margin-bottom:16px;">
                <b style="font-size:1.1rem;letter-spacing:.05em">DESVÍOS POR SECTOR</b></div>""", unsafe_allow_html=True)

            sector_total = df_d.groupby("Sector").size()
            sector_dev   = df_d[df_d["es_desvio"]].groupby("Sector").size()
            sector_tasa  = (sector_dev / sector_total * 100).round(1).sort_values(ascending=False)

            st.markdown("""<table style="width:100%;border-collapse:collapse;">
                <tr style="background:#1A2C5B;color:white;">
                    <th style="padding:10px;text-align:left">Sector</th>
                    <th style="padding:10px;text-align:center">Registros</th>
                    <th style="padding:10px;text-align:center">Desvíos</th>
                    <th style="padding:10px;text-align:center">% Desvío</th>
                    <th style="padding:10px;text-align:left">  </th>
                </tr>""" + "".join([
                f"""<tr style="background:{'#f5f5f5' if i%2==0 else 'white'};">
                    <td style="padding:10px;border-left:4px solid {'#C0392B' if v>15 else '#E67E22' if v>10 else '#27AE60'}">{s}</td>
                    <td style="padding:10px;text-align:center">{sector_total.get(s,0)}</td>
                    <td style="padding:10px;text-align:center">{sector_dev.get(s,0)}</td>
                    <td style="padding:10px;text-align:center;font-weight:700;color:{'#C0392B' if v>15 else '#E67E22' if v>10 else '#27AE60'}">{v}%</td>
                    <td style="padding:10px;width:200px"><div style="background:{'#C0392B' if v>15 else '#E67E22' if v>10 else '#27AE60'};height:16px;width:{min(v*5,200)}px;border-radius:4px"></div></td>
                </tr>""" for i,(s,v) in enumerate(sector_tasa.items())
            ]) + "</table>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── SECCIÓN 4: TOP 5 DELEGADOS ──
            st.markdown("""<div style="background:#1A2C5B;color:white;padding:12px 20px;border-radius:8px;margin-bottom:16px;">
                <b style="font-size:1.1rem;letter-spacing:.05em">TOP 5 DELEGADOS — Desvíos por persona</b></div>""", unsafe_allow_html=True)

            del_total = df_d.groupby("Nombre y Apellido").size()
            del_dev   = df_d[df_d["es_desvio"]].groupby("Nombre y Apellido").size().sort_values(ascending=False).head(5)
            del_sector= df_d.groupby("Nombre y Apellido")["Sector"].first()

            colors_rank = ["#C0392B","#8E44AD","#E67E22","#27AE60","#16A085"]
            labels_rank = ["#1","#2","#3","#4","#5"]

            for i, (nombre, n_dev) in enumerate(del_dev.items()):
                total_del = del_total.get(nombre, 1)
                pct = round(n_dev / total_del * 100, 1)
                sector = del_sector.get(nombre, "")
                color = colors_rank[i]

                # Motivos del delegado
                motivos = df_d[(df_d["Nombre y Apellido"] == nombre) & df_d["es_desvio"]]["Movilidad Gremial x Semana x Dia"].value_counts()
                motivos_txt = " · ".join([f"{m}: {c}" for m,c in motivos.head(3).items()])

                st.markdown(f"""<div style="display:flex;align-items:center;gap:16px;padding:14px;margin-bottom:10px;border:1px solid #eee;border-radius:8px;">
                    <div style="background:{color};color:white;font-weight:700;font-size:1rem;padding:12px 16px;border-radius:6px;min-width:50px;text-align:center">{labels_rank[i]}</div>
                    <div style="flex:1">
                        <div style="font-weight:700;font-size:1rem">{nombre}</div>
                        <div style="color:#666;font-size:.85rem">{sector}</div>
                        <div style="color:#888;font-size:.8rem;margin-top:4px">{motivos_txt}</div>
                    </div>
                    <div style="background:{color};color:white;font-weight:700;padding:10px 18px;border-radius:6px;text-align:center;min-width:120px">
                        {n_dev} dev. — {pct}%
                    </div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── SECCIÓN 5: DESVÍOS POR TURNO ──
            st.markdown("""<div style="background:#1A2C5B;color:white;padding:12px 20px;border-radius:8px;margin-bottom:16px;">
                <b style="font-size:1.1rem;letter-spacing:.05em">DESVÍOS POR TURNO</b></div>""", unsafe_allow_html=True)

            turnos_cols = st.columns(3)
            turnos_list = ["BLANCO","NARANJA","AMARILLO","ROT2","ROT4"]
            turno_colors = {"BLANCO":"#2980B9","NARANJA":"#E67E22","AMARILLO":"#F39C12","ROT2":"#8E44AD","ROT4":"#16A085"}

            for i, turno in enumerate(turnos_list):
                df_t = df_d[df_d["Turno"] == turno]
                if df_t.empty:
                    continue
                t_total = len(df_t)
                t_dev   = df_t["es_desvio"].sum()
                t_tasa  = round(t_dev / t_total * 100, 1) if t_total else 0
                color_t = turno_colors.get(turno, "#666")
                color_val = "#C0392B" if t_tasa > 15 else "#E67E22" if t_tasa > 10 else "#27AE60"

                with turnos_cols[i % 3]:
                    st.markdown(f"""<div style="border:1px solid #eee;border-radius:8px;padding:14px;margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <b style="color:{color_t}">TURNO {turno}</b>
                            <span style="color:{color_val};font-weight:700;font-size:1.1rem">{t_tasa}%</span>
                        </div>
                        <div style="background:#eee;border-radius:4px;height:8px;margin-bottom:8px;">
                            <div style="background:{color_val};width:{min(t_tasa*3,100)}%;height:8px;border-radius:4px"></div>
                        </div>
                        <div style="font-size:.8rem;color:#666">{t_total} registros · {t_dev} desvíos</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── EXPORTAR ──
            st.markdown("---")
            buf_ger = io.BytesIO()
            with pd.ExcelWriter(buf_ger, engine="openpyxl") as writer:
                # Resumen general
                resumen_exp = pd.DataFrame({
                    "Métrica": ["Total Registros","Total Desvíos","Tasa Desvío %","Registros Cumple"],
                    "Valor": [total, tot_dev, f"{tasa_dev}%", tot_cumple]
                })
                resumen_exp.to_excel(writer, index=False, sheet_name="Resumen")
                sector_tasa.reset_index().rename(columns={0:"Tasa %","Sector":"Sector"}).to_excel(writer, index=False, sheet_name="Por Sector")
                del_dev.reset_index().rename(columns={"Nombre y Apellido":"Delegado",0:"Desvíos"}).to_excel(writer, index=False, sheet_name="Top 5 Delegados")
                mes_tasa.reset_index().rename(columns={0:"Tasa %"}).to_excel(writer, index=False, sheet_name="Tendencia Mensual")
            buf_ger.seek(0)
            st.download_button(
                "⬇️ Exportar Dashboard a Excel",
                data=buf_ger,
                file_name=f"dashboard_gremial_{d_desde.strftime('%d%m%Y')}_{d_hasta.strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
            )



# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 6 — IMPORTAR HISTÓRICO
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "⬆️ Importar Histórico":
    st.markdown('<div class="section-title">⬆️ Importar Histórico desde Excel</div>', unsafe_allow_html=True)
    st.info("Subí tu Excel histórico. La app lee todas las solapas y toma la fecha del nombre de cada solapa automáticamente.")

    archivo = st.file_uploader("Seleccioná tu archivo Excel (.xlsx)", type=["xlsx","xls"])

    if archivo:
        try:
            xl = pd.ExcelFile(archivo)
            st.success(f"Archivo cargado: **{len(xl.sheet_names)} solapas** encontradas.")

            import re as _re

            def extraer_fecha_solapa(nombre_hoja):
                # Buscar fecha tipo 24/11, 27/04, etc. en el nombre de la solapa
                match = _re.search(r'(\d{1,2})[/\-\.](\d{1,2})', nombre_hoja)
                if match:
                    dia, mes = match.group(1), match.group(2)
                    anio = "2025" if int(mes) >= 10 else "2026"
                    try:
                        return f"{dia.zfill(2)}/{mes.zfill(2)}/{anio}"
                    except:
                        pass
                return ""

            dfs = []
            errores = []
            for hoja in xl.sheet_names:
                try:
                    # Buscar la fila con los encabezados (puede estar en fila 0 o 1)
                    df_raw = xl.parse(hoja, header=None, dtype=str)
                    header_row = 0
                    for i in range(min(3, len(df_raw))):
                        row_vals = [str(v).lower() for v in df_raw.iloc[i].values if pd.notna(v)]
                        if any("legajo" in v or "nombre" in v for v in row_vals):
                            header_row = i
                            break
                    df_h = xl.parse(hoja, header=header_row, dtype=str)
                    df_h = df_h.dropna(how="all")

                    # Mapear columnas — incluye nombres exactos de tu Excel
                    col_map = {}
                    for c in df_h.columns:
                        cl = str(c).lower().strip()
                        if "legajo" in cl: col_map[c] = "Legajo"
                        elif "nombre" in cl and "apellido" in cl: col_map[c] = "Nombre y Apellido"
                        elif "cuerpo" in cl: col_map[c] = "Cuerpo Gremial"
                        elif "sector" in cl: col_map[c] = "Sector"
                        elif "cargo" in cl: col_map[c] = "Cargo"
                        elif "turno" in cl: col_map[c] = "Turno"
                        elif "reporta" in cl: col_map[c] = "Reporta a"
                        elif "fecha" in cl: col_map[c] = "Fecha"
                        elif "movilidad" in cl: col_map[c] = "Movilidad Gremial x Semana x Dia"
                        elif "motivo" in cl and "excedencia" in cl: col_map[c] = "Motivo Excedencia"
                        elif "motivo" in cl and "licencia" in cl: col_map[c] = "Informacion Licencia"
                        elif "licencia" in cl: col_map[c] = "Licencia"
                        elif "llt" in cl or "ausencia" in cl: col_map[c] = "LLT/Ausencia Inj"
                        elif "observ" in cl: col_map[c] = "Observaciones Extras"
                        elif "motivo" in cl and "desv" in cl: col_map[c] = "Motivo (Detallar desvios)"
                        elif "accion" in cl or "acción" in cl: col_map[c] = "Accion"
                        elif "dia" in cl and "motivo" in cl: col_map[c] = "Motivo (Detallar desvios)"
                    df_h = df_h.rename(columns=col_map)

                    # Eliminar columnas duplicadas
                    df_h = df_h.loc[:, ~df_h.columns.duplicated()]

                    # Si no tiene columna Fecha, usar la fecha del nombre de la solapa
                    if "Fecha" not in df_h.columns or df_h["Fecha"].isna().all() or (df_h["Fecha"].str.strip() == "").all():
                        fecha_solapa = extraer_fecha_solapa(hoja)
                        df_h["Fecha"] = fecha_solapa

                    # Agregar columnas faltantes
                    for col in COLUMNS:
                        if col not in df_h.columns:
                            df_h[col] = ""
                    df_h = df_h[COLUMNS]
                    df_h = df_h[df_h["Nombre y Apellido"].notna() & 
                                (df_h["Nombre y Apellido"].str.strip() != "") & 
                                (df_h["Nombre y Apellido"].str.lower().str.strip() != "nombre y apellido")]
                    df_h = df_h[df_h["Legajo"].notna() & (df_h["Legajo"].str.strip() != "")]
                    # Descartar filas con "Cumple" — solo nos interesan los desvíos
                    if "Movilidad Gremial x Semana x Dia" in df_h.columns:
                        df_h = df_h[~df_h["Movilidad Gremial x Semana x Dia"].str.strip().str.lower().eq("cumple")]
                    if not df_h.empty:
                        dfs.append(df_h)
                except Exception as e:
                    errores.append(f"Solapa '{hoja}': {e}")

            if errores:
                for e in errores:
                    st.warning(f"⚠️ {e}")

            if dfs:
                df_hist = pd.concat(dfs, ignore_index=True)
                df_hist = df_hist.fillna("")
                st.markdown(f"**Vista previa — {len(df_hist)} registros encontrados en {len(dfs)} solapas:**")
                st.dataframe(df_hist.head(30), use_container_width=True)

                if st.button("✅ Confirmar importación", type="primary", use_container_width=True):
                    df_actual = load_data()
                    df_combinado = pd.concat([df_hist, df_actual], ignore_index=True)
                    df_combinado = df_combinado.drop_duplicates(subset=["Legajo","Fecha","Movilidad Gremial x Semana x Dia"], keep="last")
                    save_data(df_combinado)
                    st.success(f"✅ Importación exitosa — {len(df_combinado)} registros totales en la base.")
                    st.balloons()
            else:
                st.error("No se encontraron registros válidos en el archivo.")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — PRESENCIA DEL DÍA
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "📋 Presencia del Día":
    st.markdown('<div class="section-title">📋 Presencia del Día</div>', unsafe_allow_html=True)

    PRESENCIA_FILE = DATA_FILE.replace("registro_gremial.csv", "presencia_diaria.csv")
    ESTADOS_PRESENCIA = ["Presente", "Ausente", "Licencia", "Vacaciones"]

    def load_presencia():
        if os.path.exists(PRESENCIA_FILE):
            return pd.read_csv(PRESENCIA_FILE, dtype=str)
        return pd.DataFrame(columns=["Legajo","Nombre y Apellido","Sector","Turno","Cargo","Fecha","Estado","Observacion"])

    def save_presencia(df):
        df.to_csv(PRESENCIA_FILE, index=False)

    # ── Filtros ──
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        fecha_sel = st.date_input("📅 Fecha", value=date.today(), format="DD/MM/YYYY", key="fecha_presencia")
        fecha_str = fecha_sel.strftime("%d/%m/%Y")
    with f2:
        fil_turno = st.selectbox("Turno", ["Todos","BLANCO","NARANJA","AMARILLO","ROT2","ROT4"], key="fil_turno_pres")
    with f3:
        fil_cargo = st.selectbox("Cargo", ["Todos","CIR","Delegado"], key="fil_cargo_pres")
    with f4:
        fil_sector_pres = st.selectbox("Sector", ["Todos"] + SECTORES_OPTS, key="fil_sector_pres")

    df_pres = load_presencia()
    df_hoy = df_pres[df_pres["Fecha"] == fecha_str].copy() if not df_pres.empty else pd.DataFrame()

    # Construir lista base desde DELEGADOS
    lista_base = []
    for leg, d in DELEGADOS.items():
        estado_actual = "Presente"
        obs_actual = ""
        if not df_hoy.empty:
            fila = df_hoy[df_hoy["Legajo"] == leg]
            if not fila.empty:
                estado_actual = fila.iloc[0]["Estado"]
                obs_actual = fila.iloc[0].get("Observacion", "")
        lista_base.append({
            "Legajo": leg,
            "Nombre y Apellido": d["nombre"],
            "Sector": d["sector"],
            "Turno": d["turno"],
            "Cargo": d["cargo"],
            "Estado": estado_actual,
            "Observacion": obs_actual,
        })
    df_base = pd.DataFrame(lista_base)

    # Aplicar filtros
    df_filtrado = df_base.copy()
    if fil_turno != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Turno"] == fil_turno]
    if fil_cargo != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Cargo"] == fil_cargo]
    if fil_sector_pres != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Sector"] == fil_sector_pres]

    # ── Carga automática desde fichadas WD ──
    st.markdown("**📂 Cargar fichadas WD (opcional)**")
    fichadas_file = st.file_uploader("Subí el Excel de fichadas del día", type=["xlsx","xls"], key="fichadas_wd")
    if fichadas_file:
        try:
            df_fich = pd.read_excel(fichadas_file, dtype=str)
            # Normalizar columna legajo
            col_legajo_fich = None
            for c in df_fich.columns:
                if "legajo" in str(c).lower():
                    col_legajo_fich = c
                    break
            if col_legajo_fich:
                legajos_fichados = set(df_fich[col_legajo_fich].dropna().str.strip().tolist())
                # Actualizar presencia en df_base
                def estado_desde_fichada(leg):
                    return "Presente" if str(leg).strip() in legajos_fichados else "Ausente"
                df_base["Estado"] = df_base["Legajo"].apply(estado_desde_fichada)
                presentes = (df_base["Estado"] == "Presente").sum()
                ausentes  = (df_base["Estado"] == "Ausente").sum()
                st.success(f"✅ Fichadas cargadas — {presentes} presentes, {ausentes} ausentes. Podés corregir manualmente abajo si alguien está de licencia o vacaciones.")
            else:
                st.error("No se encontró columna Legajo en el archivo.")
        except Exception as e:
            st.error(f"Error al leer fichadas: {e}")

    st.caption(f"Mostrando {len(df_filtrado)} delegados para el {fecha_str}")

    # ── Tabla de carga compacta ──
    nuevos_registros = []
    with st.form("form_presencia"):
        # Header
        h1,h2,h3,h4,h5,h6 = st.columns([3,2,1,1,2,2])
        h1.markdown("**Nombre**"); h2.markdown("**Sector**"); h3.markdown("**Turno**")
        h4.markdown("**Cargo**"); h5.markdown("**Estado**"); h6.markdown("**Observación**")
        st.divider()

        for _, row in df_filtrado.sort_values(["Turno","Nombre y Apellido"]).iterrows():
            c1,c2,c3,c4,c5,c6 = st.columns([3,2,1,1,2,2])
            c1.write(row["Nombre y Apellido"])
            c2.write(row["Sector"])
            c3.write(row["Turno"])
            c4.write(row["Cargo"])
            est_idx = ESTADOS_PRESENCIA.index(row["Estado"]) if row["Estado"] in ESTADOS_PRESENCIA else 0
            estado = c5.selectbox("", ESTADOS_PRESENCIA, index=est_idx, key=f"est_{row['Legajo']}", label_visibility="collapsed")
            obs    = c6.text_input("", value=row["Observacion"], key=f"obs_{row['Legajo']}", placeholder="Opcional", label_visibility="collapsed")
            nuevos_registros.append({
                "Legajo": row["Legajo"],
                "Nombre y Apellido": row["Nombre y Apellido"],
                "Sector": row["Sector"],
                "Turno": row["Turno"],
                "Cargo": row["Cargo"],
                "Fecha": fecha_str,
                "Estado": estado,
                "Observacion": obs,
            })

        if st.form_submit_button("💾 Guardar Presencia", type="primary", use_container_width=True):
            df_nuevos = pd.DataFrame(nuevos_registros)
            # Reconstruir todos los delegados del día (no solo los filtrados)
            lista_completa = []
            for leg, d in DELEGADOS.items():
                match = [r for r in nuevos_registros if r["Legajo"] == leg]
                if match:
                    lista_completa.append(match[0])
                else:
                    # Si no estaba en el filtro, mantener estado anterior
                    if not df_hoy.empty:
                        fila = df_hoy[df_hoy["Legajo"] == leg]
                        if not fila.empty:
                            lista_completa.append(fila.iloc[0].to_dict())
                            continue
                    lista_completa.append({
                        "Legajo": leg, "Nombre y Apellido": d["nombre"],
                        "Sector": d["sector"], "Turno": d["turno"],
                        "Cargo": d["cargo"], "Fecha": fecha_str,
                        "Estado": "Presente", "Observacion": ""
                    })
            df_nuevos_full = pd.DataFrame(lista_completa)
            if not df_pres.empty:
                df_pres = df_pres[df_pres["Fecha"] != fecha_str]
            df_pres = pd.concat([df_pres, df_nuevos_full], ignore_index=True)
            save_presencia(df_pres)
            st.success(f"✅ Presencia del {fecha_str} guardada.")
            st.rerun()

    # ── Resumen del día ──
    st.markdown("---")
    if not df_hoy.empty:
        r1, r2, r3, r4 = st.columns(4)
        r1.markdown(f'<div class="kpi-card ok"><div class="kpi-label">Presentes</div><div class="kpi-value">{(df_hoy["Estado"]=="Presente").sum()}</div></div>', unsafe_allow_html=True)
        r2.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Ausentes</div><div class="kpi-value">{(df_hoy["Estado"]=="Ausente").sum()}</div></div>', unsafe_allow_html=True)
        r3.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Licencia</div><div class="kpi-value">{(df_hoy["Estado"]=="Licencia").sum()}</div></div>', unsafe_allow_html=True)
        r4.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Vacaciones</div><div class="kpi-value">{(df_hoy["Estado"]=="Vacaciones").sum()}</div></div>', unsafe_allow_html=True)

        df_no_pres = df_hoy[df_hoy["Estado"] != "Presente"]
        if not df_no_pres.empty:
            st.markdown("**⚠️ No presentes:**")
            st.dataframe(df_no_pres[["Nombre y Apellido","Turno","Sector","Cargo","Estado","Observacion"]].reset_index(drop=True), use_container_width=True)
    else:
        st.info("Guardá la presencia para ver el resumen.")
