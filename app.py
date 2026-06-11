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
    "7232":  {"nombre": "Daniel Coronel",           "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division", "cargo": "CIR",      "turno": "BLANCO",   "reporta": "Mauro Bringas"},
    "12738": {"nombre": "Nadia Pasaban",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "CIR",      "turno": "NARANJA",  "reporta": "Juan Bizzotto"},
    "605097":{"nombre": "Luciana Dominguez",         "cuerpo": "MH",                 "sector": "MH Division",             "cargo": "CIR",      "turno": "BLANCO",   "reporta": "Martin Gentilini"},
    "8266":  {"nombre": "Esteban Vilches",           "cuerpo": "MH",                 "sector": "Motores Division",        "cargo": "CIR",      "turno": "NARANJA",  "reporta": "Carlos Fuentes"},
    "5555":  {"nombre": "Pablo Lafalce",             "cuerpo": "PINTURA",            "sector": "Pintura Division",        "cargo": "CIR",      "turno": "AMARILLO", "reporta": "Matias Cardenas"},
    "10018": {"nombre": "Lucia Dana Messa",          "cuerpo": "QC",                 "sector": "QC Division",             "cargo": "CIR",      "turno": "AMARILLO", "reporta": "Marcelo Martinez"},
    "7047":  {"nombre": "Walter Gonzalez",           "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division","cargo": "CIR",   "turno": "NARANJA",  "reporta": "Hugo Taboada"},
    "7652":  {"nombre": "Matias Giroldi",            "cuerpo": "SOLDADURA",          "sector": "Welding Division",        "cargo": "CIR",      "turno": "AMARILLO", "reporta": "Faustino Carrasco"},
    "12538": {"nombre": "Noelia Celeste Benitez",    "cuerpo": "SOLDADURA",          "sector": "Ensamble Chasis Division","cargo": "CIR",      "turno": "BLANCO",   "reporta": "Leonardo Gonzalez"},
    "9600":  {"nombre": "Nicolas Emanuel Said",      "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Chasis Division","cargo": "Delegado", "turno": "AMARILLO", "reporta": "Jose Gorosito"},
    "13264": {"nombre": "Micaela Mazzoni",           "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division", "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Andres Galdames"},
    "1772":  {"nombre": "Miguel Guaraz",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division", "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Cristian Moreno"},
    "6306":  {"nombre": "Guillermo Ojeda",           "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division", "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Fernando Camerhoff"},
    "7688":  {"nombre": "Mariano Brazuna",           "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division", "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Fernando Camerhoff"},
    "8248":  {"nombre": "Jeronimo Blais",            "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division", "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Jose Ibañer"},
    "5228":  {"nombre": "Leandro Escudero",          "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division", "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Walter Herrero"},
    "675":   {"nombre": "Gabriel Horizon",           "cuerpo": "MANTENIMIENTO",      "sector": "Ensamble Final Division", "cargo": "Delegado", "turno": "ROT2",     "reporta": ""},
    "1446":  {"nombre": "Victor Gomez",              "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Esteban Kroger"},
    "12398": {"nombre": "Lourdes Anabella Escobar",  "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Facundo Bustos"},
    "12422": {"nombre": "Valeria Soledad Gonzalez",  "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Facundo Bustos"},
    "6607":  {"nombre": "Nestor Peralta",            "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Juan Bizzotto"},
    "1602":  {"nombre": "Nestor Bonuccelli",         "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Marcos Furtado"},
    "12338": {"nombre": "Lucrecia Silvana Guanca",   "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Marcos Furtado"},
    "4583":  {"nombre": "Damian Gomez",              "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Marcos Furtado"},
    "9667":  {"nombre": "Maylen Diaz",               "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",  "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Maximiliano Blemberger"},
    "604590":{"nombre": "Aldana Cabello",            "cuerpo": "SOLDADURA",          "sector": "Frame Division",          "cargo": "Delegado", "turno": "AMARILLO", "reporta": ""},
    "7001":  {"nombre": "Alexis Alvarez",            "cuerpo": "SOLDADURA",          "sector": "Frame Division",          "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Martin Poropat"},
    "9566":  {"nombre": "Braian Campodonico",        "cuerpo": "SOLDADURA",          "sector": "Frame Division",          "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Federico Rulat"},
    "6713":  {"nombre": "Lucas Montani",             "cuerpo": "SOLDADURA",          "sector": "Frame Division",          "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Sebastian Crisa"},
    "4729":  {"nombre": "Gerardo Rebora",            "cuerpo": "MH",                 "sector": "MH Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Jose Mateo"},
    "5783":  {"nombre": "Arnoldo Acuna Cutzoni",     "cuerpo": "MH",                 "sector": "MH Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Martin Gentilini"},
    "9398":  {"nombre": "Nicolas Sequeira",          "cuerpo": "MH",                 "sector": "MH Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Nazareno Cubilla"},
    "6268":  {"nombre": "Bruno Saquejo",             "cuerpo": "MH",                 "sector": "MH Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Emanuel Plas"},
    "13400": {"nombre": "Viviana Pura",              "cuerpo": "MH",                 "sector": "MH Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ramiro Elizaga"},
    "4583b": {"nombre": "Genaro Augurio",            "cuerpo": "MH",                 "sector": "MH Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Jose Mateo"},
    "8198":  {"nombre": "Martin Malacalza Portillo", "cuerpo": "ENSAMBLE & MOTORES", "sector": "Motores Division",        "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Cesar Cuenca"},
    "1983":  {"nombre": "Diego Cardozo",             "cuerpo": "MH",                 "sector": "Motores Division",        "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Carlos Fuentes"},
    "837":   {"nombre": "Pablo Bruchez",             "cuerpo": "PINTURA",            "sector": "Pintura Division",        "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Matias Cardenas"},
    "6717":  {"nombre": "Hector Gonzalez",           "cuerpo": "PINTURA",            "sector": "Pintura Division",        "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Ariel Rupp"},
    "6606":  {"nombre": "Juan Seery",                "cuerpo": "PINTURA",            "sector": "Pintura Division",        "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Javier Werner"},
    "11878": {"nombre": "Valeria Soledad Villalba",  "cuerpo": "PINTURA",            "sector": "Pintura Division",        "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Javier Werner"},
    "8273":  {"nombre": "Matias Rosales",            "cuerpo": "PINTURA",            "sector": "Pintura Division",        "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Cesar Bentancur"},
    "1748":  {"nombre": "Ezequiel Marquez",          "cuerpo": "PINTURA",            "sector": "Pintura Division",        "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Javier Werner"},
    "573":   {"nombre": "Horacio Gutierrez",         "cuerpo": "MANTENIMIENTO",      "sector": "Pintura Division",        "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Nicolas Echeverria"},
    "4394":  {"nombre": "Diego Quintana",            "cuerpo": "SOLDADURA",          "sector": "Press Division",          "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Julian Lopez"},
    "4310":  {"nombre": "Nestor Uran",               "cuerpo": "QC",                 "sector": "QC Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Marcelo Martinez"},
    "5740":  {"nombre": "Enrique Schmidt",           "cuerpo": "QC",                 "sector": "QC Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Ariel Sena"},
    "4934":  {"nombre": "Leonardo Montiel",          "cuerpo": "QC",                 "sector": "QC Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ariel Sena"},
    "8536":  {"nombre": "Ariel Mora",                "cuerpo": "QC",                 "sector": "QC Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ruben Barrera"},
    "1645":  {"nombre": "Nicolas Martin",            "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division","cargo": "Delegado","turno": "AMARILLO","reporta": "Diego Vargas"},
    "12376": {"nombre": "Yesica Soledad Guereñu",    "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division","cargo": "Delegado","turno": "AMARILLO","reporta": "Diego Irrassuegui"},
    "1858":  {"nombre": "Daniel Marcelli",           "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division","cargo": "Delegado","turno": "BLANCO", "reporta": "Matias Medina"},
    "12643": {"nombre": "Sabrina Denis",             "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division","cargo": "Delegado","turno": "BLANCO", "reporta": "Carlos Demierre"},
    "7264":  {"nombre": "Jordan Cirigliano",         "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division","cargo": "Delegado","turno": "NARANJA","reporta": "Jose Martinez"},
    "7942":  {"nombre": "Fernando Albornoz",         "cuerpo": "SOLDADURA",          "sector": "Welding Division",        "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Diego Mendieta"},
    "605098":{"nombre": "Isaia Lopez Rinaldi",       "cuerpo": "SOLDADURA",          "sector": "Welding Division",        "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Leonardo Gonzalez"},
    "6650":  {"nombre": "Pablo Lazarsky",            "cuerpo": "SOLDADURA",          "sector": "Welding Division",        "cargo": "Delegado", "turno": "BLANCO",   "reporta": ""},
    "7092":  {"nombre": "Juan Roa",                  "cuerpo": "SOLDADURA",          "sector": "Welding Division",        "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Federico Medina"},
    "9412":  {"nombre": "Lucas Alvarez",             "cuerpo": "SOLDADURA",          "sector": "Welding Division",        "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Juan Lindner"},
    "8235":  {"nombre": "Mariano Figueroa",          "cuerpo": "MANTENIMIENTO",      "sector": "Welding Division",        "cargo": "Delegado", "turno": "ROT4",     "reporta": "Victor Garcia Calderon"},
}

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
        "", ["➕ Cargar Registro", "📊 Reportes", "📈 Dashboard Gerencial", "📁 Ver / Editar Datos", "⬆️ Importar Histórico", "⬇️ Exportar Excel"],
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

    # Selector por nombre con búsqueda
    nombres_lista = ["— Seleccioná un delegado —"] + [f"{leg} · {d['nombre']}" for leg, d in sorted(DELEGADOS.items(), key=lambda x: x[1]['nombre'])]
    sel = st.selectbox("👤 Buscar delegado", nombres_lista)

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


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 5 — DASHBOARD GERENCIAL
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "📈 Dashboard Gerencial":
    df_all = load_data()
    st.markdown('<div class="section-title">📈 Dashboard Gerencial</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("Aún no hay registros cargados.")
    else:
        df_all["_fecha"] = pd.to_datetime(df_all["Fecha"], dayfirst=True, errors="coerce")

        # Filtro de período
        pc1, pc2 = st.columns(2)
        with pc1:
            d_desde = st.date_input("Desde", value=date.today() - timedelta(days=30), format="DD/MM/YYYY", key="dash_desde")
        with pc2:
            d_hasta = st.date_input("Hasta", value=date.today(), format="DD/MM/YYYY", key="dash_hasta")

        df_d = df_all[(df_all["_fecha"] >= pd.Timestamp(d_desde)) & (df_all["_fecha"] <= pd.Timestamp(d_hasta))].copy()

        if df_d.empty:
            st.warning("No hay datos en ese período.")
        else:
            DESVIOS = ["No Cumple","Excede -5min","Excede 5/10 min","Excede + 10/20min","Supera + 1/2hs","SUPERA SEMANA COMPLETA","GENERA PDL"]
            LICENCIAS_ACTIVAS = ["ENFERMEDAD INCULPABLE","ART","JUDICIALIDAD","VACACIONES","Paternidad/Maternidad","PARO/MOVILIZACIÓN","FALLECIMIENTO FAMILIAR"]
            AUSENCIAS = ["LLT SIN AVISO","AUSENCIA INJ","AUSENCIA JUSTI"]

            df_d["es_desvio"]   = df_d["Movilidad Gremial x Semana x Dia"].isin(DESVIOS)
            df_d["es_licencia"] = df_d["Licencia"].isin(LICENCIAS_ACTIVAS)
            df_d["es_ausencia"] = df_d["LLT/Ausencia Inj"].isin(AUSENCIAS)
            df_d["es_presente"] = (~df_d["es_licencia"]) & (~df_d["es_ausencia"])

            total_reg   = len(df_d)
            tot_desvios = df_d["es_desvio"].sum()
            tot_licencias = df_d["es_licencia"].sum()
            tot_ausencias = df_d["es_ausencia"].sum()
            tot_presentes = df_d["es_presente"].sum()
            pct_cumple = round((df_d["Movilidad Gremial x Semana x Dia"] == "Cumple").sum() / total_reg * 100) if total_reg else 0

            # ── KPIs ──
            k1,k2,k3,k4,k5 = st.columns(5)
            with k1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total registros</div><div class="kpi-value">{total_reg}</div></div>', unsafe_allow_html=True)
            with k2:
                st.markdown(f'<div class="kpi-card ok"><div class="kpi-label">% Cumplimiento</div><div class="kpi-value">{pct_cumple}%</div></div>', unsafe_allow_html=True)
            with k3:
                st.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Desvíos</div><div class="kpi-value">{tot_desvios}</div></div>', unsafe_allow_html=True)
            with k4:
                st.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Licencias</div><div class="kpi-value">{tot_licencias}</div></div>', unsafe_allow_html=True)
            with k5:
                st.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Ausencias</div><div class="kpi-value">{tot_ausencias}</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            col_a, col_b = st.columns(2)

            # ── Ranking de desvíos por delegado ──
            with col_a:
                st.markdown("**🚨 Ranking de Desvíos por Delegado**")
                ranking = df_d[df_d["es_desvio"]].groupby("Nombre y Apellido").size().sort_values(ascending=False).head(15)
                if ranking.empty:
                    st.success("Sin desvíos en el período 🎉")
                else:
                    st.bar_chart(ranking)

            # ── Presentes vs Ausentes vs Licencias ──
            with col_b:
                st.markdown("**👥 Estado de Delegados (registros del período)**")
                estado_counts = pd.Series({
                    "Presentes": int(tot_presentes),
                    "Licencias": int(tot_licencias),
                    "Ausencias": int(tot_ausencias),
                })
                st.bar_chart(estado_counts)

            st.markdown("---")
            col_c, col_d = st.columns(2)

            # ── Evolución semanal por sector ──
            with col_c:
                st.markdown("**📅 Evolución Semanal de Desvíos por Sector**")
                df_d["Semana"] = df_d["_fecha"].dt.to_period("W").astype(str)
                evo_sector = df_d[df_d["es_desvio"]].groupby(["Semana","Sector"]).size().unstack(fill_value=0)
                if evo_sector.empty:
                    st.success("Sin desvíos en el período 🎉")
                else:
                    st.line_chart(evo_sector)

            # ── Comparativa entre sectores ──
            with col_d:
                st.markdown("**🏭 Comparativa entre Sectores**")
                comp = df_d.groupby("Sector").agg(
                    Total=("Nombre y Apellido","count"),
                    Desvios=("es_desvio","sum"),
                    Licencias=("es_licencia","sum"),
                ).sort_values("Desvios", ascending=False)
                comp["% Cumplimiento"] = ((comp["Total"] - comp["Desvios"]) / comp["Total"] * 100).round(1).astype(str) + "%"
                st.dataframe(comp, use_container_width=True)

            st.markdown("---")

            # ── Licencias activas ──
            st.markdown("**📋 Licencias Activas en el Período**")
            df_lic = df_d[df_d["es_licencia"]][["Nombre y Apellido","Sector","Turno","Licencia","Informacion Licencia","Fecha"]].copy()
            df_lic = df_lic.sort_values("Fecha", ascending=False)
            if df_lic.empty:
                st.success("No hay licencias activas en el período.")
            else:
                st.dataframe(df_lic.reset_index(drop=True), use_container_width=True)

            st.markdown("---")

            # ── Tabla resumen por delegado ──
            st.markdown("**📊 Resumen Completo por Delegado**")
            resumen_ger = df_d.groupby(["Nombre y Apellido","Sector","Turno"]).agg(
                Registros=("Fecha","count"),
                Cumple=("Movilidad Gremial x Semana x Dia", lambda x: (x=="Cumple").sum()),
                Desvios=("es_desvio","sum"),
                Licencias=("es_licencia","sum"),
                Ausencias=("es_ausencia","sum"),
            ).reset_index()
            resumen_ger["% OK"] = (resumen_ger["Cumple"] / resumen_ger["Registros"] * 100).round(1).astype(str) + "%"
            resumen_ger = resumen_ger.sort_values("Desvios", ascending=False)
            st.dataframe(resumen_ger, use_container_width=True, height=400)

            # Exportar reporte gerencial
            buf_ger = io.BytesIO()
            with pd.ExcelWriter(buf_ger, engine="openpyxl") as writer:
                resumen_ger.to_excel(writer, index=False, sheet_name="Resumen Gerencial")
                df_lic.to_excel(writer, index=False, sheet_name="Licencias Activas")
                if not evo_sector.empty:
                    evo_sector.to_excel(writer, sheet_name="Evolución Semanal")
            buf_ger.seek(0)
            st.download_button(
                "⬇️ Descargar Reporte Gerencial",
                data=buf_ger,
                file_name=f"reporte_gerencial_{d_desde.strftime('%d%m%Y')}_{d_hasta.strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 6 — IMPORTAR HISTÓRICO
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "⬆️ Importar Histórico":
    st.markdown('<div class="section-title">⬆️ Importar Histórico desde Excel</div>', unsafe_allow_html=True)
    st.info("Subí tu Excel con el historial anterior. La app lee todas las solapas automáticamente y unifica todo con los registros actuales.")

    archivo = st.file_uploader("Seleccioná tu archivo Excel (.xlsx)", type=["xlsx","xls"])

    if archivo:
        try:
            xl = pd.ExcelFile(archivo)
            st.success(f"Archivo cargado: **{len(xl.sheet_names)} solapas** encontradas: {', '.join(xl.sheet_names)}")

            dfs = []
            errores = []
            for hoja in xl.sheet_names:
                try:
                    df_h = xl.parse(hoja, dtype=str)
                    df_h = df_h.dropna(how="all")
                    # Mapear columnas flexiblemente
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
                        elif "licencia" in cl and "info" not in cl: col_map[c] = "Licencia"
                        elif "info" in cl and "licencia" in cl: col_map[c] = "Informacion Licencia"
                        elif "llt" in cl or "ausencia" in cl: col_map[c] = "LLT/Ausencia Inj"
                        elif "observ" in cl: col_map[c] = "Observaciones Extras"
                        elif "motivo" in cl and "desv" in cl: col_map[c] = "Motivo (Detallar desvios)"
                        elif "accion" in cl or "acción" in cl: col_map[c] = "Accion"
                        elif "dia" in cl and "motivo" in cl: col_map[c] = "Motivo (Detallar desvios)"
                    df_h = df_h.rename(columns=col_map)
                    # Agregar columnas faltantes
                    for col in COLUMNS:
                        if col not in df_h.columns:
                            df_h[col] = ""
                    df_h = df_h[COLUMNS]
                    df_h = df_h[df_h["Nombre y Apellido"].notna() & (df_h["Nombre y Apellido"].str.strip() != "") & (df_h["Nombre y Apellido"].str.lower() != "nombre y apellido")]
                    dfs.append(df_h)
                except Exception as e:
                    errores.append(f"Solapa '{hoja}': {e}")

            if errores:
                for e in errores:
                    st.warning(f"⚠️ {e}")

            if dfs:
                df_hist = pd.concat(dfs, ignore_index=True)
                df_hist = df_hist.fillna("")
                st.markdown(f"**Vista previa — {len(df_hist)} registros encontrados:**")
                st.dataframe(df_hist.head(20), use_container_width=True)

                if st.button("✅ Confirmar importación", type="primary", use_container_width=True):
                    df_actual = load_data()
                    df_combinado = pd.concat([df_hist, df_actual], ignore_index=True)
                    df_combinado = df_combinado.drop_duplicates(subset=["Legajo","Fecha","Movilidad Gremial x Semana x Dia"], keep="last")
                    save_data(df_combinado)
                    st.success(f"✅ Importación exitosa — {len(df_combinado)} registros totales en la base.")
                    st.balloons()
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
