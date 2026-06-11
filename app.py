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

    hoy = date.today()
    fecha_sel = st.date_input("📅 Fecha", value=hoy, format="DD/MM/YYYY", key="fecha_presencia")
    fecha_str = fecha_sel.strftime("%d/%m/%Y")

    df_pres = load_presencia()
    df_hoy = df_pres[df_pres["Fecha"] == fecha_str] if not df_pres.empty else pd.DataFrame()

    # Construir lista base desde DELEGADOS
    lista_base = []
    for leg, d in DELEGADOS.items():
        estado_actual = ""
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
            "Estado": estado_actual if estado_actual else "Presente",
            "Observacion": obs_actual,
        })
    df_base = pd.DataFrame(lista_base)

    # Mostrar por turno
    turnos_orden = ["BLANCO", "NARANJA", "AMARILLO", "ROT2", "ROT4"]
    nuevos_registros = []

    with st.form("form_presencia"):
        for turno in turnos_orden:
            df_turno = df_base[df_base["Turno"] == turno]
            if df_turno.empty:
                continue

            st.markdown(f"### 🔵 Turno {turno} — {len(df_turno)} delegados")
            cols_header = st.columns([3, 2, 2, 2, 2])
            cols_header[0].markdown("**Nombre**")
            cols_header[1].markdown("**Sector**")
            cols_header[2].markdown("**Cargo**")
            cols_header[3].markdown("**Estado**")
            cols_header[4].markdown("**Observación**")

            for _, row in df_turno.iterrows():
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
                c1.write(row["Nombre y Apellido"])
                c2.write(row["Sector"])
                c3.write(row["Cargo"])
                est_idx = ESTADOS_PRESENCIA.index(row["Estado"]) if row["Estado"] in ESTADOS_PRESENCIA else 0
                estado = c4.selectbox("", ESTADOS_PRESENCIA, index=est_idx, key=f"est_{row['Legajo']}")
                obs = c5.text_input("", value=row["Observacion"], key=f"obs_{row['Legajo']}", placeholder="Opcional")
                nuevos_registros.append({
                    "Legajo": row["Legajo"],
                    "Nombre y Apellido": row["Nombre y Apellido"],
                    "Sector": row["Sector"],
                    "Turno": turno,
                    "Cargo": row["Cargo"],
                    "Fecha": fecha_str,
                    "Estado": estado,
                    "Observacion": obs,
                })
            st.markdown("---")

        if st.form_submit_button("💾 Guardar Presencia del Día", type="primary", use_container_width=True):
            df_nuevos = pd.DataFrame(nuevos_registros)
            # Reemplazar registros del día
            if not df_pres.empty:
                df_pres = df_pres[df_pres["Fecha"] != fecha_str]
            df_pres = pd.concat([df_pres, df_nuevos], ignore_index=True)
            save_presencia(df_pres)
            st.success(f"✅ Presencia del {fecha_str} guardada — {len(df_nuevos)} delegados registrados.")
            st.rerun()

    # ── Vista resumen ──
    st.markdown("---")
    st.markdown(f"**📊 Resumen del {fecha_str}**")
    if not df_hoy.empty:
        resumen_pres = df_hoy.groupby(["Turno","Estado"]).size().unstack(fill_value=0)
        st.dataframe(resumen_pres, use_container_width=True)

        # Ausentes y licencias destacados
        df_ausentes = df_hoy[df_hoy["Estado"].isin(["Ausente","Licencia","Vacaciones"])]
        if not df_ausentes.empty:
            st.markdown("**⚠️ No presentes hoy:**")
            st.dataframe(df_ausentes[["Nombre y Apellido","Turno","Sector","Cargo","Estado","Observacion"]].reset_index(drop=True), use_container_width=True)
        else:
            st.success("✅ Todos los delegados presentes hoy.")
    else:
        st.info("Aún no se cargó la presencia para esta fecha.")
