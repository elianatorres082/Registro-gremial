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
    .app-header {
        background: linear-gradient(135deg, #1A2C5B 0%, #2E4A9E 100%);
        color: white !important;
        padding: 1.4rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
        display: flex; align-items: center; gap: 1rem;
    }
    .app-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; color: white !important; }
    .app-header p  { margin: 0; font-size: 0.85rem; opacity: 0.75; color: white !important; }
    .kpi-card { border-radius: 10px; padding: 1.1rem 1.4rem; border-left: 4px solid #2E4A9E; margin-bottom: .5rem; }
    .kpi-card.warning { border-left-color: #E8A020; }
    .kpi-card.danger  { border-left-color: #C0392B; }
    .kpi-card.ok      { border-left-color: #27AE60; }
    .kpi-label { font-size: .75rem; text-transform: uppercase; letter-spacing: .05em; opacity: .7; }
    .kpi-value { font-size: 2rem; font-weight: 700; line-height: 1.1; }
    .section-title { font-size: 1rem; font-weight: 600; border-bottom: 2px solid #2E4A9E; padding-bottom: .3rem; margin-bottom: 1rem; }
    section[data-testid="stSidebar"] { background: #1A2C5B !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BASE DE DELEGADOS — SMATA PLANTA
# ═══════════════════════════════════════════════════════════════════════════════
DELEGADOS = {
    "7232":   {"nombre": "Daniel Coronel",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "CIR",      "turno": "BLANCO",   "reporta": "Mauro Bringas"},
    "12738":  {"nombre": "Nadia Pasaban",               "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "CIR",      "turno": "NARANJA",  "reporta": "Juan Bizzotto"},
    "605097": {"nombre": "Luciana Dominguez",           "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "CIR",      "turno": "BLANCO",   "reporta": "Martin Gentilini"},
    "8266":   {"nombre": "Esteban Vilches",             "cuerpo": "MH",                 "sector": "Motores Division",             "cargo": "CIR",      "turno": "NARANJA",  "reporta": "Carlos Fuentes"},
    "10018":  {"nombre": "Lucia Dana Messa",            "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "CIR",      "turno": "AMARILLO", "reporta": "Marcelo Martinez"},
    "7047":   {"nombre": "Walter Gonzalez",             "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "CIR",      "turno": "NARANJA",  "reporta": "Hugo Taborda"},
    "7652":   {"nombre": "Matias Giroldi",              "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "CIR",      "turno": "AMARILLO", "reporta": "Faustino Carrasco"},
    "12538":  {"nombre": "Noelia Celeste Benitez",      "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "CIR",      "turno": "BLANCO",   "reporta": "Leonardo Gonzalez"},
    "9500":   {"nombre": "Nicolas Emanuel Said",        "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Chasis Division",     "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Jose Gorosito"},
    "13264":  {"nombre": "Micaela Mazzoni",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Andres Galdames"},
    "1772":   {"nombre": "Miguel Guaraz",               "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Cristian Moreno"},
    "6306":   {"nombre": "Guillermo Ojeda",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Fernando Canerhoff"},
    "7888":   {"nombre": "Mariano Brazuna",             "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Fernando Canerhoff"},
    "8248":   {"nombre": "Jeronimo Blois",              "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Jose Ibanez"},
    "5228":   {"nombre": "Leandro Escudero",            "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Walter Herrero"},
    "3675":   {"nombre": "Gabriel Monzon",              "cuerpo": "MANTENIMIENTO",      "sector": "Ensamble Final Division",      "cargo": "Delegado", "turno": "ROT2",     "reporta": "Ariel Amarillo"},
    "1446":   {"nombre": "Victor Gomez",                "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Esteban Kroger"},
    "12398":  {"nombre": "Lourdes Anabella Escobar",    "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Facundo Bustos"},
    "12422":  {"nombre": "Valeria Soledad Gonzalez",    "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Facundo Bustos"},
    "6807":   {"nombre": "Nestor Peralta",              "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Juan Bizzotto"},
    "1802":   {"nombre": "Nestor Bonuccelli",           "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Marcos Furtado"},
    "12338":  {"nombre": "Lucrecia Silvana Guanca",     "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Marcos Furtado"},
    "4553":   {"nombre": "Damian Gomez",                "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Marcos Furtado"},
    "9667":   {"nombre": "Maylen Albelo",               "cuerpo": "ENSAMBLE & MOTORES", "sector": "Ensamble TRIM Division",       "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Maximiliano Ellemberger"},
    "604590": {"nombre": "Aldana Cabello",              "cuerpo": "SOLDADURA",          "sector": "Frame Division",               "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Pablo Lopez"},
    "7001":   {"nombre": "Alexis Alvarez",              "cuerpo": "SOLDADURA",          "sector": "Frame Division",               "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Pablo Lopez"},
    "9565":   {"nombre": "Braian Campodonico",          "cuerpo": "SOLDADURA",          "sector": "Frame Division",               "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Edmundo Lugo"},
    "6713":   {"nombre": "Lucas Montani",               "cuerpo": "SOLDADURA",          "sector": "Frame Division",               "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ignacio Ibar"},
    "4729":   {"nombre": "Gerardo Rebora",              "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Jose Mateo"},
    "6783":   {"nombre": "Arnolfo Acuna Culzoni",       "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Martin Gentilini"},
    "6287":   {"nombre": "Bruno Sanjurjo",              "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Emanuel Pacher"},
    "13400":  {"nombre": "Viviana Pura",                "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ramiro Elizaga"},
    "4583":   {"nombre": "Genaro Augurio",              "cuerpo": "MH",                 "sector": "MH Division",                  "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Jose Mateo"},
    "8193":   {"nombre": "Martin Malacalza Portillo",   "cuerpo": "ENSAMBLE & MOTORES", "sector": "Motores Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Cesar Cuenca"},
    "1983":   {"nombre": "Diego Cardozo",               "cuerpo": "MH",                 "sector": "Motores Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Carlos Fuentes"},
    "837":    {"nombre": "Pablo Bruchez",               "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Matias Cardenas"},
    "6717":   {"nombre": "Hector Gonzalez",             "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Ariel Rupp"},
    "6825":   {"nombre": "Juan Seery",                  "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Javier Werner"},
    "11878":  {"nombre": "Valeria Soledad Villalba",    "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Javier Werner"},
    "8273":   {"nombre": "Matias Rosales",              "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Cesar Bentancur"},
    "1748":   {"nombre": "Ezequiel Marquez",            "cuerpo": "PINTURA",            "sector": "Pintura Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Javier Werner"},
    "573":    {"nombre": "Horacio Gutierrez",           "cuerpo": "MANTENIMIENTO",      "sector": "Pintura Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Nicolas Echeverria"},
    "4394":   {"nombre": "Diego Quintana",              "cuerpo": "SOLDADURA",          "sector": "Press Division",               "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Julian Lopez"},
    "4310":   {"nombre": "Nestor Uran",                 "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Marcelo Martinez"},
    "5740":   {"nombre": "Enrique Schmidt",             "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Ariel Sena"},
    "4934":   {"nombre": "Leonardo Montiel",            "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Ariel Sena"},
    "8641":   {"nombre": "Ariel Monzon",                "cuerpo": "QC",                 "sector": "QC Division",                  "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Ruben Ragusa"},
    "1645":   {"nombre": "Nicolas Martin",              "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Diego Vargas"},
    "12376":  {"nombre": "Yesica Soledad Guereñu",      "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Diego Irasuegui"},
    "1858":   {"nombre": "Daniel Marcell",              "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Matias Medina"},
    "12643":  {"nombre": "Sabrina Denis",               "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Carlos Demierre"},
    "7264":   {"nombre": "Jordan Cirigliano",           "cuerpo": "EXTERNOS",           "sector": "Servicio al Cliente Division", "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Jose Martinez"},
    "7942":   {"nombre": "Fernando Albornoz",           "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "AMARILLO", "reporta": "Diego Mendieta"},
    "605098": {"nombre": "Iara Lopez Rinaldi",          "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Leonardo Gonzalez"},
    "6650":   {"nombre": "Pablo Lasansky",              "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "BLANCO",   "reporta": "Juan Lindner"},
    "7092":   {"nombre": "Juan Roa",                    "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Federico Medina"},
    "9412":   {"nombre": "Lucas Alvarez",               "cuerpo": "SOLDADURA",          "sector": "Welding Division",             "cargo": "Delegado", "turno": "NARANJA",  "reporta": "Faustino Carrasco"},
    "8235":   {"nombre": "Mariano Figueroa",            "cuerpo": "MANTENIMIENTO",      "sector": "Welding Division",             "cargo": "Delegado", "turno": "ROT4",     "reporta": "Victor Garcia Calderon"},
}

# Padrón vacío para las nuevas solapas — completar con datos reales
DELEGADOS_FDP    = {}   # SMATA Fuera de Planta
DELEGADOS_ASIMRA = {}   # ASIMRA

# ── Opciones de formulario ────────────────────────────────────────────────────
MOVILIDAD_OPTS = [
    "No Cumple", "Excede -5min", "Excede 5/10 min",
    "Excede + 10/20min", "Supera + 1/2hs", "SUPERA SEMANA COMPLETA",
    "GENERA PDL", "Cambia de turno",
]
# Lista canónica de desvíos — ÚNICA fuente de verdad para Reportes y Dashboard
# Lista canónica de desvíos — incluye variantes reales del CSV (strip+lower al comparar)
DESVIOS = [
    "No Cumple",
    "Excede -5min",
    "Excede 5/10 min",
    "Excede + 10/20min",
    "Supera + 1/2hs",
    "SUPERA SEMANA COMPLETA",
    "Supera semanal",
    "GENERA PDL",
    "Cambia de turno",
    "No realiza actividad gremial",
]
# Para comparación robusta (strip + lower)
DESVIOS_NORM = [d.strip().lower() for d in DESVIOS]

def es_desvio(val):
    return str(val).strip().lower() in DESVIOS_NORM
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
    "Ensamble Chasis Division", "Ensamble Final Division", "Ensamble TRIM Division",
    "Frame Division", "MH Division", "Motores Division", "Pintura Division",
    "Press Division", "QC Division", "Servicio al Cliente Division", "Welding Division", "Otro",
]
ESTADOS_PRESENCIA = ["Presente", "Pendiente", "Ausente", "Licencia", "Vacaciones"]
COLUMNS = [
    "Legajo", "Nombre y Apellido", "Cuerpo Gremial", "Sector", "Cargo",
    "Turno", "Reporta a", "Fecha",
    "Movilidad Gremial x Semana x Dia", "Motivo Excedencia",
    "Licencia", "Informacion Licencia",
    "LLT/Ausencia Inj", "Observaciones Extras",
    "Motivo (Detallar desvios)", "Accion",
]

# ── Rutas de datos ─────────────────────────────────────────────────────────────
TEAMS_PATH = r"C:\users\Eliana.Torres\OneDrive - Toyota Argentina S.A\HR PLANT - Seguimiento gremial 2026"
if os.path.isdir(TEAMS_PATH):
    DATA_DIR = TEAMS_PATH
else:
    _base = os.path.expanduser("~")
    _onedrive = None
    for _d in os.listdir(_base):
        _full = os.path.join(_base, _d)
        if "onedrive" in _d.lower() and "toyota" in _d.lower() and os.path.isdir(_full):
            _onedrive = _full
            break
    if _onedrive:
        _teams = os.path.join(_onedrive, "HR PLANT - Seguimiento gremial 2026")
        DATA_DIR = _teams if os.path.isdir(_teams) else _onedrive
    else:
        DATA_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE          = os.path.join(DATA_DIR, "registro_gremial.csv")
PRESENCIA_FILE     = os.path.join(DATA_DIR, "presencia_diaria.csv")
PADRON_FILE        = os.path.join(DATA_DIR, "padron_delegados.csv")
DATA_FILE_FDP      = os.path.join(DATA_DIR, "registro_fuera_de_planta.csv")
DATA_FILE_ASIMRA   = os.path.join(DATA_DIR, "registro_asimra.csv")
PADRON_FDP_FILE    = os.path.join(DATA_DIR, "padron_fdp.csv")
PADRON_ASIMRA_FILE = os.path.join(DATA_DIR, "padron_asimra.csv")

# ── Helpers de persistencia ───────────────────────────────────────────────────
def _parsear_fechas(df, col="Fecha"):
    """
    Parseo robusto de fechas. Maneja:
      - dd/mm/YYYY  dd/mm/yy  YYYY-mm-dd  YYYY-mm-dd HH:MM:SS
      - d/m/YYYY (sin ceros)
      - Texto libre como "1/6/2026 y 02/06/2026" -> toma el primer match
    """
    import re as _re
    def _parse_one(val):
        s = str(val).strip()
        if s in ("", "nan", "NaT", "None"):
            return pd.NaT
        # Extraer primer patrón de fecha del texto
        m = _re.search(r"(\d{1,4})[/\-\.](\d{1,2})[/\-\.](\d{2,4})", s)
        if not m:
            return pd.NaT
        a, b, c = m.group(1), m.group(2), m.group(3)
        # YYYY-MM-DD
        if len(a) == 4:
            try: return pd.Timestamp(int(a), int(b), int(c))
            except: return pd.NaT
        # DD/MM/YYYY o DD/MM/YY
        if len(c) == 4:
            try: return pd.Timestamp(int(c), int(b), int(a))
            except: return pd.NaT
        if len(c) == 2:
            yr = 2000 + int(c)
            try: return pd.Timestamp(yr, int(b), int(a))
            except: return pd.NaT
        return pd.NaT
    return df[col].apply(_parse_one)

def _get_mtime(fp):
    """Devuelve el mtime del archivo para usar como cache key."""
    try: return os.path.getmtime(fp)
    except: return 0

@st.cache_data
def load_data(filepath=None, _mtime=None):
    """
    _mtime se pasa como parámetro para invalidar el cache cuando el archivo cambia.
    Streamlit ignora parámetros que empiezan con _ para el hashing del cache.
    """
    fp = filepath or DATA_FILE
    if os.path.exists(fp):
        df = pd.read_csv(fp, dtype=str)
        for c in COLUMNS:
            if c not in df.columns:
                df[c] = ""
        df = df[COLUMNS].fillna("")
        # Normalizar espacios para que el matching con DESVIOS sea robusto
        df["Movilidad Gremial x Semana x Dia"] = df["Movilidad Gremial x Semana x Dia"].str.strip()
        return df
    return pd.DataFrame(columns=COLUMNS)

def save_data(df, filepath=None):
    fp = filepath or DATA_FILE
    df.to_csv(fp, index=False)
    load_data.clear()  # invalida cache para que el dashboard vea los datos nuevos

def load_presencia():
    if os.path.exists(PRESENCIA_FILE):
        return pd.read_csv(PRESENCIA_FILE, dtype=str)
    return pd.DataFrame(columns=["Legajo","Nombre y Apellido","Sector","Turno","Cargo","Fecha","Estado","Observacion"])

def save_presencia(df):
    df.to_csv(PRESENCIA_FILE, index=False)

PADRON_COLS = ["Legajo","Nombre y Apellido","Cuerpo Gremial","Sector","Cargo","Turno","Reporta a",
               "Fecha Alta","Fecha Baja","Motivo Baja","Activo"]

def load_padron():
    if os.path.exists(PADRON_FILE):
        df = pd.read_csv(PADRON_FILE, dtype=str)
        for c in PADRON_COLS:
            if c not in df.columns:
                df[c] = ""
        return df[PADRON_COLS].fillna("")
    # Primera vez: construir desde DELEGADOS
    rows = []
    for leg, d in DELEGADOS.items():
        rows.append({"Legajo": leg, "Nombre y Apellido": d["nombre"],
            "Cuerpo Gremial": d["cuerpo"], "Sector": d["sector"],
            "Cargo": d["cargo"], "Turno": d["turno"], "Reporta a": d["reporta"],
            "Fecha Alta": "", "Fecha Baja": "", "Motivo Baja": "", "Activo": "Sí"})
    return pd.DataFrame(rows, columns=PADRON_COLS)

def save_padron(df):
    df.to_csv(PADRON_FILE, index=False)

PADRON_EXT_COLS = ["Legajo","Nombre y Apellido","Sector","Cargo","Turno","Reporta a",
                   "Fecha Alta","Fecha Baja","Motivo Baja","Activo"]

def load_padron_ext(filepath):
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, dtype=str)
        for c in PADRON_EXT_COLS:
            if c not in df.columns:
                df[c] = ""
        return df[PADRON_EXT_COLS].fillna("")
    return pd.DataFrame(columns=PADRON_EXT_COLS)

def save_padron_ext(df, filepath):
    df.to_csv(filepath, index=False)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div style="font-size:2.2rem">🏭</div>
  <div>
    <h1>Registro de Bloque Gremial</h1>
    <p>Control de movilidad gremial · Toyota Argentina</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATOS HARDCODEADOS — SMATA FUERA DE PLANTA (histórico desde Excel)
# ═══════════════════════════════════════════════════════════════════════════════
# Status posibles: "Activo", "Desvinculado", "Reincorporado a TASA", "Cargo Político"
SMATA_FDP_HISTORICO = [
    {"legajo":"595",  "nombre":"Firpo Bruno",          "cargo_gremial":"Consejo Directivo",                                    "desde":"2008", "status":"Desvinculado",         "detalle":"Baja 26-05-2026"},
    {"legajo":"884",  "nombre":"Gomez Alejandro",       "cargo_gremial":"Colaborador Sub Delegación Baradero",                  "desde":"2011", "status":"Activo",               "detalle":""},
    {"legajo":"2322", "nombre":"Morelli Santiago",      "cargo_gremial":"Secretario Delegación",                               "desde":"2013", "status":"Reincorporado a TASA", "detalle":"Mayo 2025"},
    {"legajo":"1250", "nombre":"Ghiglione Marcelo",     "cargo_gremial":"Delegación Zárate",                                   "desde":"2013", "status":"Reincorporado a TASA", "detalle":"Abril 2018"},
    {"legajo":"717",  "nombre":"Karg Miguel",           "cargo_gremial":"Comisión Directiva",                                  "desde":"2011", "status":"Fallecimiento",         "detalle":"17/06/2026"},
    {"legajo":"609",  "nombre":"Sanzio Esteban",        "cargo_gremial":"Intendente Baradero",                                 "desde":"2012", "status":"Cargo Político",       "detalle":"Intendente Baradero"},
    {"legajo":"1549", "nombre":"Baraybar Martin",       "cargo_gremial":"Colaborador Sub Delegación Baradero",                  "desde":"2012", "status":"Activo",               "detalle":""},
    {"legajo":"2505", "nombre":"Franzanti Andres",      "cargo_gremial":"Comisión Directiva - Secretario Gral. Delegación",    "desde":"2016", "status":"Desvinculado",         "detalle":"Diciembre 2025"},
    {"legajo":"2072", "nombre":"Romero Hector Nicolas", "cargo_gremial":"Colaborador Sub Delegación Baradero",                  "desde":"2017", "status":"Reincorporado a TASA", "detalle":"Posible salida"},
    {"legajo":"1471", "nombre":"Arocena Pablo",         "cargo_gremial":"COHISE - Colaborador Delegación Zárate",              "desde":"2020", "status":"Activo",               "detalle":""},
    {"legajo":"4740", "nombre":"Beckman Matias David",  "cargo_gremial":"Gestión Hotel SMATA Mendoza",                         "desde":"2020", "status":"Activo",               "detalle":""},
    {"legajo":"269",  "nombre":"Rosendo Ariel",         "cargo_gremial":"Cargo Político",                                      "desde":"2011", "status":"Desvinculado",         "detalle":"Febrero 2023"},
    {"legajo":"3412", "nombre":"Moreira Nicolas",       "cargo_gremial":"Secretario de Cultura, Educación, Turismo y Deporte", "desde":"2020", "status":"Activo",               "detalle":"Baradero"},
    {"legajo":"2833", "nombre":"Sansoni Edgardo",       "cargo_gremial":"Comisión Directiva - Coordinador",                    "desde":"2016", "status":"Reincorporado a TASA", "detalle":"Febrero 2023"},
    {"legajo":"1535", "nombre":"Leguizamon Hernan",     "cargo_gremial":"Colaborador SMATA Central (Acción Social)",           "desde":"2023", "status":"Activo",               "detalle":""},
    {"legajo":"4756", "nombre":"Gauto Francisco Rodolfo","cargo_gremial":"Colaborador SMATA Central (Gremiales)",              "desde":"2023", "status":"Activo",               "detalle":""},
    {"legajo":"6443", "nombre":"Raul Chavez",           "cargo_gremial":"Colaborador Delegación Zárate",                       "desde":"2025", "status":"Activo",               "detalle":""},
    {"legajo":"5555", "nombre":"Pablo Lafalce",         "cargo_gremial":"Colaborador Delegación Baradero",                     "desde":"2026", "status":"Activo",               "detalle":"Desde 20-04-2026"},
    {"legajo":"",     "nombre":"Nicolas Sequeira",        "cargo_gremial":"Delegado SMATA Planta",                               "desde":"",     "status":"Renuncia Sindicato",    "detalle":"Continua como TM en TASA"},
]

# ═══════════════════════════════════════════════════════════════════════════════
# DATOS HARDCODEADOS — ASIMRA
# ═══════════════════════════════════════════════════════════════════════════════
ASIMRA_PADRON = [
    {"legajo":"337",  "nombre":"Alejandro Galeano",  "cargo_gremial":"CIR",       "posicion_org":"Seccional Campana"},
    {"legajo":"344",  "nombre":"Carlos Gutierrez",   "cargo_gremial":"CIR",       "posicion_org":"Secretario Unión Zárate/Campana"},
    {"legajo":"1427", "nombre":"Franco Ferreyra",    "cargo_gremial":"CIR",       "posicion_org":"Comité Interno"},
    {"legajo":"453",  "nombre":"Fernando Arriola",   "cargo_gremial":"CIR",       "posicion_org":"Seccional Campana"},
    {"legajo":"569",  "nombre":"Juan De Cia",        "cargo_gremial":"Delegado",  "posicion_org":""},
    {"legajo":"1686", "nombre":"Jonatan Colaso",     "cargo_gremial":"Delegado",  "posicion_org":""},
    {"legajo":"6110", "nombre":"Jose Monetta",       "cargo_gremial":"Delegado",  "posicion_org":""},
]

# ── Mandatos vigentes por sindicato ──────────────────────────────────────────
MANDATOS = {
    "SMATA Planta":         {"inicio": "18/11/2025", "fin_estimado": "18/11/2028", "periodo": "2025-2028"},
    "SMATA Fuera de Planta":{"inicio": "18/11/2025", "fin_estimado": "18/11/2028", "periodo": "2025-2028"},
    "ASIMRA":               {"inicio": "",            "fin_estimado": "",           "periodo": ""},
}

# ── Archivos de datos para FDP/ASIMRA (solo por si se quiere persistir ediciones) ──
PADRON_FDP_FILE    = os.path.join(DATA_DIR, "padron_fdp.csv")
PADRON_ASIMRA_FILE = os.path.join(DATA_DIR, "padron_asimra.csv")

def _load_fdp():
    """Carga padrón FDP desde CSV si existe, sino usa los datos hardcodeados."""
    if os.path.exists(PADRON_FDP_FILE):
        df = pd.read_csv(PADRON_FDP_FILE, dtype=str).fillna("")
        return df
    return pd.DataFrame(SMATA_FDP_HISTORICO)

def _save_fdp(df):
    df.to_csv(PADRON_FDP_FILE, index=False)

def _load_asimra():
    if os.path.exists(PADRON_ASIMRA_FILE):
        df = pd.read_csv(PADRON_ASIMRA_FILE, dtype=str).fillna("")
        return df
    return pd.DataFrame(ASIMRA_PADRON)

def _save_asimra(df):
    df.to_csv(PADRON_ASIMRA_FILE, index=False)

# ── placeholder para que no rompa nada que todavía referencie _render_seccion_externa ──
def _render_seccion_externa(titulo, emoji, data_file, padron_file, key_prefix):
    st.markdown(f'<div class="section-title">{titulo}</div>', unsafe_allow_html=True)
    tab_reg, tab_rep, tab_pad = st.tabs(["➕ Registro Diario", "Reportes", "👥 Padrón"])

    df_ext     = load_data(data_file)
    df_pad_ext = load_padron_ext(padron_file)

    # ── REGISTRO DIARIO ──
    with tab_reg:
        activos_ext = df_pad_ext[df_pad_ext["Activo"]=="Sí"] if not df_pad_ext.empty else pd.DataFrame()
        if activos_ext.empty:
            st.info(f"No hay delegados en el padrón de {titulo}. Agregalos en la solapa **Padrón** primero.")
        else:
            opts_ext = ["— Seleccioná —"] + [f"{r['Legajo']} · {r['Nombre y Apellido']}" for _, r in activos_ext.iterrows()]
            sel_ext  = st.selectbox("Delegado", opts_ext, key=f"{key_prefix}_sel")
            leg_ext, dat_ext = "", {}
            if sel_ext != "— Seleccioná —":
                leg_ext = sel_ext.split(" · ")[0]
                dat_ext = activos_ext[activos_ext["Legajo"]==leg_ext].iloc[0].to_dict()
                st.success(f"✅ **{dat_ext['Nombre y Apellido']}** — {dat_ext.get('Sector','')} | Turno: {dat_ext.get('Turno','')}")
        with st.form(f"form_{key_prefix}"):
            c1,c2,c3 = st.columns(3)
            with c1:
                legajo  = st.text_input("Legajo *", value=leg_ext if 'leg_ext' in dir() else "", key=f"{key_prefix}_leg")
                nombre  = st.text_input("Nombre y Apellido *", value=dat_ext.get("Nombre y Apellido","") if 'dat_ext' in dir() else "", key=f"{key_prefix}_nom")
                cuerpo  = st.text_input("Cuerpo Gremial", value=titulo, key=f"{key_prefix}_cb")
            with c2:
                sv = dat_ext.get("Sector", SECTORES_OPTS[0]) if 'dat_ext' in dir() else SECTORES_OPTS[0]
                sector  = st.selectbox("Sector", SECTORES_OPTS, index=SECTORES_OPTS.index(sv) if sv in SECTORES_OPTS else 0, key=f"{key_prefix}_sec")
                cargo   = st.text_input("Cargo", value=dat_ext.get("Cargo","Delegado") if 'dat_ext' in dir() else "Delegado", key=f"{key_prefix}_car")
                tv = dat_ext.get("Turno", TURNO_OPTS[0]) if 'dat_ext' in dir() else TURNO_OPTS[0]
                turno   = st.selectbox("Turno", TURNO_OPTS, index=TURNO_OPTS.index(tv) if tv in TURNO_OPTS else 0, key=f"{key_prefix}_tur")
            with c3:
                reporta = st.text_input("Reporta a", value=dat_ext.get("Reporta a","") if 'dat_ext' in dir() else "", key=f"{key_prefix}_rep")
                fecha   = st.date_input("Fecha *", value=date.today(), format="DD/MM/YYYY", key=f"{key_prefix}_fec")
            st.markdown("**📍 Movilidad y Excedencia**")
            mc1,mc2 = st.columns(2)
            with mc1: movilidad  = st.selectbox("Movilidad Gremial", MOVILIDAD_OPTS, key=f"{key_prefix}_mov")
            with mc2: motivo_exc = st.selectbox("Motivo Excedencia", MOTIVO_EXCEDENCIA_OPTS, key=f"{key_prefix}_mex")
            st.markdown("**📋 Licencias / Ausencias**")
            lc1,lc2,lc3 = st.columns(3)
            with lc1: licencia = st.selectbox("Licencia", LICENCIAS_OPTS, key=f"{key_prefix}_lic")
            with lc2: info_lic = st.text_input("Información Licencia", key=f"{key_prefix}_ilic")
            with lc3: llt      = st.selectbox("LLT / Ausencia Inj.", LLT_OPTS, key=f"{key_prefix}_llt")
            st.markdown("**💬 Observaciones y Acción**")
            oc1,oc2,oc3 = st.columns(3)
            with oc1: obs_extra   = st.text_area("Observaciones", height=80, key=f"{key_prefix}_obs")
            with oc2: motivo_desv = st.text_area("Motivo Desvíos", height=80, key=f"{key_prefix}_mds")
            with oc3: accion      = st.selectbox("Acción", ACCION_OPTS, key=f"{key_prefix}_acc")
            if st.form_submit_button("💾 Guardar Registro", type="primary", use_container_width=True):
                if not legajo or not nombre:
                    st.error("Completá Legajo y Nombre.")
                else:
                    nuevo = {"Legajo":legajo.strip(),"Nombre y Apellido":nombre.strip(),"Cuerpo Gremial":cuerpo,
                        "Sector":sector,"Cargo":cargo,"Turno":turno,"Reporta a":reporta,
                        "Fecha":fecha.strftime("%d/%m/%Y"),"Movilidad Gremial x Semana x Dia":movilidad,
                        "Motivo Excedencia":motivo_exc,"Licencia":licencia,"Informacion Licencia":info_lic,
                        "LLT/Ausencia Inj":llt,"Observaciones Extras":obs_extra,
                        "Motivo (Detallar desvios)":motivo_desv,"Accion":accion}
                    df_ext = pd.concat([df_ext, pd.DataFrame([nuevo])], ignore_index=True)
                    save_data(df_ext, data_file)
                    if es_desvio(movilidad): st.error(f"🚨 Guardado — **{nombre}**: {movilidad}")
                    else: st.success(f"✅ Guardado — **{nombre}**")

    # ── REPORTES ──
    with tab_rep:
        df_rep = load_data(data_file)
        if df_rep.empty:
            st.info("Sin registros cargados.")
        else:
            df_rep["_fecha"] = _parsear_fechas(df_rep)
            fv = df_rep["_fecha"].dropna()
            fmin = fv.min().date() if not fv.empty else date.today()
            fmax = fv.max().date() if not fv.empty else date.today()
            rd1,rd2 = st.columns(2)
            with rd1: r_desde = st.date_input("Desde", value=fmin, format="DD/MM/YYYY", key=f"{key_prefix}_rd")
            with rd2: r_hasta = st.date_input("Hasta", value=fmax, format="DD/MM/YYYY", key=f"{key_prefix}_rh")
            df_rf = df_rep[(df_rep["_fecha"]>=pd.Timestamp(r_desde))&(df_rep["_fecha"]<=pd.Timestamp(r_hasta))].copy()
            df_rf["_es_desvio"] = df_rf["Movilidad Gremial x Semana x Dia"].apply(es_desvio)
            tot   = int(df_rf["_es_desvio"].sum())
            afect = int(df_rf[df_rf["_es_desvio"]]["Nombre y Apellido"].nunique())
            reinc = int((df_rf[df_rf["_es_desvio"]].groupby("Nombre y Apellido").size() >= 3).sum())
            k1,k2,k3 = st.columns(3)
            k1.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Total Desvíos</div><div class="kpi-value">{tot}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Afectados</div><div class="kpi-value">{afect}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="kpi-card {"danger" if reinc>0 else "ok"}"><div class="kpi-label">Reincidentes</div><div class="kpi-value">{reinc}</div></div>', unsafe_allow_html=True)
            if tot > 0:
                st.markdown("---")
                dt = df_rf[df_rf["_es_desvio"]].groupby("Nombre y Apellido").size().sort_values(ascending=False).reset_index()
                dt.columns = ["Nombre y Apellido","Desvíos"]
                st.dataframe(dt, use_container_width=True)
            buf_r = io.BytesIO()
            with pd.ExcelWriter(buf_r, engine="openpyxl") as w:
                df_rf.drop(columns=["_fecha","_es_desvio"],errors="ignore").to_excel(w,index=False,sheet_name="Registros")
            buf_r.seek(0)
            st.download_button("⬇️ Exportar", data=buf_r,
                file_name=f"{key_prefix}_{r_desde.strftime('%d%m%Y')}_{r_hasta.strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ── PADRÓN ──
    with tab_pad:
        st.markdown(f"### 👥 Padrón {titulo}")
        df_pad_ext = load_padron_ext(padron_file)
        activos_p  = df_pad_ext[df_pad_ext["Activo"]=="Sí"] if not df_pad_ext.empty else pd.DataFrame()
        st.markdown(f"**{len(activos_p)} representantes activos**")
        if not activos_p.empty:
            st.dataframe(activos_p.reset_index(drop=True), use_container_width=True, height=280)
        st.markdown("---")
        st.markdown("**➕ Alta**")
        with st.form(f"form_alta_{key_prefix}"):
            pa1,pa2,pa3 = st.columns(3)
            with pa1:
                p_leg = st.text_input("Legajo *", key=f"{key_prefix}_aleg")
                p_nom = st.text_input("Nombre y Apellido *", key=f"{key_prefix}_anom")
            with pa2:
                p_sec = st.selectbox("Sector", SECTORES_OPTS, key=f"{key_prefix}_asec")
                p_car = st.text_input("Cargo", value="Delegado", key=f"{key_prefix}_acar")
                p_tur = st.selectbox("Turno", TURNO_OPTS, key=f"{key_prefix}_atur")
            with pa3:
                p_rep = st.text_input("Reporta a", key=f"{key_prefix}_arep")
                p_fec = st.date_input("Fecha Alta", value=date.today(), format="DD/MM/YYYY", key=f"{key_prefix}_afec")
            if st.form_submit_button("✅ Registrar Alta", type="primary"):
                if not p_leg or not p_nom:
                    st.error("Completá Legajo y Nombre.")
                else:
                    nueva = pd.DataFrame([{"Legajo":p_leg.strip(),"Nombre y Apellido":p_nom.strip(),
                        "Sector":p_sec,"Cargo":p_car,"Turno":p_tur,"Reporta a":p_rep,
                        "Fecha Alta":p_fec.strftime("%d/%m/%Y"),"Fecha Baja":"","Motivo Baja":"","Activo":"Sí"}])
                    df_pad_ext = pd.concat([df_pad_ext, nueva], ignore_index=True)
                    save_padron_ext(df_pad_ext, padron_file)
                    st.success(f"✅ Alta: {p_nom}"); st.rerun()
        if not activos_p.empty:
            st.markdown("**🔴 Baja**")
            sel_b = st.selectbox("Delegado a dar de baja",
                (activos_p["Legajo"]+" · "+activos_p["Nombre y Apellido"]).tolist(), key=f"{key_prefix}_bsel")
            leg_b = sel_b.split(" · ")[0]
            with st.form(f"form_baja_{key_prefix}"):
                bb1,bb2 = st.columns(2)
                with bb1: fb = st.date_input("Fecha Baja", value=date.today(), format="DD/MM/YYYY", key=f"{key_prefix}_bfec")
                with bb2: mb = st.text_input("Motivo *", key=f"{key_prefix}_bmot")
                if st.form_submit_button("🔴 Confirmar Baja", type="primary"):
                    if not mb:
                        st.error("Ingresá el motivo.")
                    else:
                        idx_b = df_pad_ext[df_pad_ext["Legajo"]==leg_b].index
                        df_pad_ext.loc[idx_b,"Fecha Baja"] = fb.strftime("%d/%m/%Y")
                        df_pad_ext.loc[idx_b,"Motivo Baja"] = mb
                        df_pad_ext.loc[idx_b,"Activo"] = "No"
                        save_padron_ext(df_pad_ext, padron_file)
                        st.success("🔴 Baja registrada."); st.rerun()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Navegación")
    pagina = st.radio("", [
        "Cargar Registro",
        "Presencia del Dia",
        "Reportes",
        "Dashboard Gerencial",
        "Padron Delegados",
        "Ver y Editar Datos",
        "Importar Historico",
        "Exportar Excel",
        "SMATA Fuera de Planta",
        "ASIMRA",
        "Historial Gremial",
        "Generar Reporte PPT",
    ], label_visibility="collapsed")
    st.markdown("---")
    df_all = load_data(_mtime=_get_mtime(DATA_FILE))
    st.markdown(f"**Total registros:** {len(df_all)}")
    if not df_all.empty:
        try:
            ult = _parsear_fechas(df_all).dropna()
            if not ult.empty:
                st.markdown(f"**Última carga:** {ult.max().strftime('%d/%m/%Y')}")
        except Exception:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — CARGAR REGISTRO
# ═══════════════════════════════════════════════════════════════════════════════
if pagina == "Cargar Registro":
    st.markdown('<div class="section-title">Nuevo Registro Diario</div>', unsafe_allow_html=True)

    CUERPOS_OPTS = sorted(set(d["cuerpo"] for d in DELEGADOS.values()))
    f1, f2 = st.columns(2)
    with f1:
        cuerpo_filtro = st.selectbox("🤝 Filtrar por Cuerpo Gremial", ["Todos"] + CUERPOS_OPTS, key="filtro_cuerpo")
    with f2:
        if cuerpo_filtro == "Todos":
            delegados_filtrados = sorted(DELEGADOS.items(), key=lambda x: x[1]['nombre'])
        else:
            delegados_filtrados = sorted([(k,v) for k,v in DELEGADOS.items() if v['cuerpo'] == cuerpo_filtro], key=lambda x: x[1]['nombre'])
        nombres_lista = ["— Seleccioná un delegado —"] + [f"{leg} · {d['nombre']}" for leg, d in delegados_filtrados]
        sel = st.selectbox("👤 Seleccioná el delegado", nombres_lista, key="sel_delegado")

    if sel != "— Seleccioná un delegado —":
        leg_auto = sel.split(" · ")[0]
        delegado_data = DELEGADOS.get(leg_auto, {})
    else:
        leg_auto, delegado_data = "", {}

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
        with mc1: movilidad  = st.selectbox("Movilidad Gremial x Semana x Día *", MOVILIDAD_OPTS)
        with mc2: motivo_exc = st.selectbox("Motivo Excedencia", MOTIVO_EXCEDENCIA_OPTS)

        st.markdown("**📋 Licencias / Ausencias**")
        lc1, lc2, lc3 = st.columns(3)
        with lc1: licencia = st.selectbox("Licencia", LICENCIAS_OPTS)
        with lc2: info_lic = st.text_input("Información Licencia")
        with lc3: llt      = st.selectbox("LLT / Ausencia Inj.", LLT_OPTS)

        st.markdown("**💬 Observaciones y Acción**")
        oc1, oc2, oc3 = st.columns(3)
        with oc1: obs_extra   = st.text_area("Observaciones Extras", height=80)
        with oc2: motivo_desv = st.text_area("Motivo (Detallar desvíos)", height=80)
        with oc3: accion      = st.selectbox("Acción", ACCION_OPTS)

        submitted = st.form_submit_button("💾 Guardar Registro", use_container_width=True, type="primary")

    if submitted:
        if not legajo or not nombre:
            st.error("⚠️ Completá al menos Legajo y Nombre.")
        else:
            nuevo = {"Legajo": legajo.strip(), "Nombre y Apellido": nombre.strip(),
                "Cuerpo Gremial": cuerpo, "Sector": sector, "Cargo": cargo,
                "Turno": turno, "Reporta a": reporta, "Fecha": fecha.strftime("%d/%m/%Y"),
                "Movilidad Gremial x Semana x Dia": movilidad, "Motivo Excedencia": motivo_exc,
                "Licencia": licencia, "Informacion Licencia": info_lic, "LLT/Ausencia Inj": llt,
                "Observaciones Extras": obs_extra, "Motivo (Detallar desvios)": motivo_desv, "Accion": accion}
            df_all = load_data(_mtime=_get_mtime(DATA_FILE))
            df_all = pd.concat([df_all, pd.DataFrame([nuevo])], ignore_index=True)
            save_data(df_all)
            if es_desvio(movilidad):
                st.error(f"🚨 Registro guardado — **{nombre}**: {movilidad} (excedencia detectada).")
            else:
                st.success(f"✅ Registro guardado — **{nombre}**.")


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — REPORTES
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "Reportes":
    df_all = load_data(_mtime=_get_mtime(DATA_FILE))
    st.markdown('<div class="section-title">Reporte Gerencial de Desvíos</div>', unsafe_allow_html=True)
    if df_all.empty:
        st.info("Aún no hay registros cargados.")
    else:
        df_all["_fecha"] = _parsear_fechas(df_all)
        fechas_validas = df_all["_fecha"].dropna()
        fecha_min = fechas_validas.min().date() if not fechas_validas.empty else date.today()
        fecha_max = fechas_validas.max().date() if not fechas_validas.empty else date.today()

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
            sel_jefe = st.selectbox("Reporta a (Supervisor)", jefes_op, key="rep_jefe")

        fd1, fd2 = st.columns(2)
        with fd1: f_desde = st.date_input("Desde", value=fecha_min, format="DD/MM/YYYY", key="rep_desde")
        with fd2: f_hasta = st.date_input("Hasta", value=fecha_max, format="DD/MM/YYYY", key="rep_hasta")

        # Filtrar siempre desde el df_all (recalculado en cada interacción de Streamlit)
        df_f = df_all[
            (df_all["_fecha"] >= pd.Timestamp(f_desde)) & (df_all["_fecha"] <= pd.Timestamp(f_hasta))
        ].copy()
        if sel_sector != "Todos": df_f = df_f[df_f["Sector"] == sel_sector]
        if sel_del    != "Todos": df_f = df_f[df_f["Nombre y Apellido"] == sel_del]
        if sel_jefe   != "Todos": df_f = df_f[df_f["Reporta a"] == sel_jefe]
        df_f["_es_desvio"] = df_f["Movilidad Gremial x Semana x Dia"].apply(es_desvio)

        tot_dev   = int(df_f["_es_desvio"].sum())
        del_afect = int(df_f[df_f["_es_desvio"]]["Nombre y Apellido"].nunique())
        reincid   = int((df_f[df_f["_es_desvio"]].groupby("Nombre y Apellido").size() >= 3).sum())
        sector_top = df_f[df_f["_es_desvio"]]["Sector"].value_counts().idxmax() if tot_dev > 0 else "—"

        k1,k2,k3,k4 = st.columns(4)
        k1.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Total Desvíos</div><div class="kpi-value">{tot_dev}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Delegados afectados</div><div class="kpi-value">{del_afect}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi-card {"danger" if reincid>0 else "ok"}"><div class="kpi-label">Reincidentes (≥3)</div><div class="kpi-value">{reincid}</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Sector más crítico</div><div class="kpi-value" style="font-size:1rem">{sector_top}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 👔 Responsabilidad por Supervisor")
        jefe_total = df_f.groupby("Reporta a").size()
        jefe_dev   = df_f[df_f["_es_desvio"]].groupby("Reporta a").size()
        jefe_df    = pd.DataFrame({"Total": jefe_total, "Desvíos": jefe_dev}).fillna(0).astype(int)
        jefe_df["Tasa %"] = (jefe_df["Desvíos"] / jefe_df["Total"] * 100).round(1)
        jefe_df["Del. con desvíos"] = df_f[df_f["_es_desvio"]].groupby("Reporta a")["Nombre y Apellido"].nunique()
        jefe_df = jefe_df.sort_values("Desvíos", ascending=False)
        for jefe, row in jefe_df.iterrows():
            if not jefe or str(jefe).strip() in ("", "nan"): continue
            tasa_j = row["Tasa %"]
            color_j = "#C0392B" if tasa_j > 20 else "#E67E22" if tasa_j > 10 else "#27AE60"
            dels_dev = df_f[(df_f["Reporta a"] == jefe) & df_f["_es_desvio"]]["Nombre y Apellido"].value_counts()
            dels_txt = " · ".join([f"{n} ({c})" for n,c in dels_dev.head(4).items()])
            st.markdown(f"""<div style="border-left:4px solid {color_j};padding:10px 16px;margin-bottom:8px;background:#fafafa;border-radius:0 8px 8px 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div><span style="font-weight:700">{jefe}</span>
                    <span style="color:#666;font-size:.8rem;margin-left:8px">{int(row.get('Del. con desvios', row.get('Del. con desvíos', 0)))} delegados con desvíos</span></div>
                    <span style="background:{color_j};color:white;padding:3px 10px;border-radius:20px;font-weight:700;font-size:.85rem">{int(row['Desvíos'])} desvíos</span>
                </div>
                <div style="color:#888;font-size:.8rem;margin-top:4px">{dels_txt}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🔁 Reincidentes — 3 o más desvíos en el período")
        dev_por_del  = df_f[df_f["_es_desvio"]].groupby("Nombre y Apellido").size().sort_values(ascending=False)
        reincidentes = dev_por_del[dev_por_del >= 3]
        if reincidentes.empty:
            st.success("✅ Sin reincidentes en el período.")
        else:
            for nombre_r, n_dev in reincidentes.items():
                grupo    = df_f[(df_f["Nombre y Apellido"] == nombre_r) & df_f["_es_desvio"]].sort_values("_fecha")
                sector_r = df_f[df_f["Nombre y Apellido"] == nombre_r]["Sector"].iloc[0]
                jefe_r   = df_f[df_f["Nombre y Apellido"] == nombre_r]["Reporta a"].iloc[0]
                turno_r  = df_f[df_f["Nombre y Apellido"] == nombre_r]["Turno"].iloc[0]
                color_r  = "#C0392B" if n_dev >= 5 else "#E67E22"
                accion_last = df_f[df_f["Nombre y Apellido"] == nombre_r]["Accion"].replace("", pd.NA).last_valid_index()
                accion_txt  = df_f.loc[accion_last, "Accion"] if accion_last is not None else "Sin acción registrada"
                fechas_dev  = " · ".join(grupo["_fecha"].dt.strftime("%d/%m").tolist())
                tipos       = grupo["Movilidad Gremial x Semana x Dia"].value_counts()
                tipos_txt   = " / ".join([f"{t}: {c}" for t,c in tipos.items()])
                st.markdown(f"""<div style="border:1px solid {color_r};border-radius:8px;padding:14px;margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                        <div><span style="font-weight:700;font-size:1rem">{nombre_r}</span><br>
                        <span style="color:#666;font-size:.8rem">{sector_r} · Turno {turno_r} · Reporta a: <b>{jefe_r}</b></span></div>
                        <span style="background:{color_r};color:white;padding:4px 14px;border-radius:20px;font-weight:700">{n_dev} desvíos</span>
                    </div>
                    <div style="font-size:.82rem;color:#444;margin-bottom:4px">📅 {fechas_dev}</div>
                    <div style="font-size:.82rem;color:#444;margin-bottom:4px">📋 {tipos_txt}</div>
                    <div style="font-size:.82rem;color:#888">⚡ {accion_txt}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        with st.expander("📋 Ver detalle completo"):
            df_desvios = df_f[df_f["_es_desvio"]].copy()
            df_desvios["_fecha_fmt"] = df_desvios["_fecha"].dt.strftime("%d/%m/%Y")
            if df_desvios.empty:
                st.success("✅ Sin desvíos.")
            else:
                for nombre_d, grupo in sorted(df_desvios.groupby("Nombre y Apellido"), key=lambda x: len(x[1]), reverse=True):
                    sector_d, turno_d, n_dev = grupo["Sector"].iloc[0], grupo["Turno"].iloc[0], len(grupo)
                    color = "#C0392B" if n_dev >= 5 else "#E67E22" if n_dev >= 3 else "#F39C12"
                    items = []
                    for _, r in grupo.sort_values("_fecha").iterrows():
                        motivo = str(r["Motivo Excedencia"]) if pd.notna(r["Motivo Excedencia"]) and str(r["Motivo Excedencia"]).strip() not in ["","NO APLICA","nan"] else ""
                        llt_v  = str(r["LLT/Ausencia Inj"]) if pd.notna(r["LLT/Ausencia Inj"]) and str(r["LLT/Ausencia Inj"]).strip() not in ["","nan"] else ""
                        obs_v  = str(r["Observaciones Extras"]) if pd.notna(r["Observaciones Extras"]) and str(r["Observaciones Extras"]).strip() not in ["","nan"] else ""
                        extra  = " · ".join([x for x in [motivo, llt_v, obs_v] if x])
                        items.append(f"<b>{r['_fecha_fmt']}</b> — {r['Movilidad Gremial x Semana x Dia']}" + (f" <span style='color:#666'>({extra})</span>" if extra else ""))
                    st.markdown(f"""<div style="border-left:4px solid {color};padding:12px 16px;margin-bottom:10px;background:#fafafa;border-radius:0 8px 8px 0;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                            <div><span style="font-weight:700">{nombre_d}</span>
                            <span style="color:#666;font-size:.85rem;margin-left:10px">{sector_d} · Turno {turno_d}</span></div>
                            <span style="background:{color};color:white;padding:4px 12px;border-radius:20px;font-weight:700;font-size:.85rem">{n_dev} desvíos</span>
                        </div>
                        <div style="font-size:.85rem;color:#444;line-height:1.8">{"<br>".join(items)}</div>
                    </div>""", unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — VER / EDITAR
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "Ver y Editar Datos":
    df_all = load_data(_mtime=_get_mtime(DATA_FILE))
    st.markdown('<div class="section-title">Tabla de Registros</div>', unsafe_allow_html=True)
    if df_all.empty:
        st.info("Aún no hay registros cargados.")
    else:
        fc1, fc2 = st.columns(2)
        with fc1: buscar  = st.text_input("🔍 Buscar por nombre o legajo", "")
        with fc2: fil_mov = st.selectbox("Filtrar por Movilidad", ["Todos"] + MOVILIDAD_OPTS)

        df_show = df_all.copy()
        if buscar:
            mask = (df_show["Nombre y Apellido"].str.contains(buscar, case=False, na=False) |
                    df_show["Legajo"].str.contains(buscar, case=False, na=False))
            df_show = df_show[mask]
        if fil_mov != "Todos":
            df_show = df_show[df_show["Movilidad Gremial x Semana x Dia"] == fil_mov]

        st.dataframe(df_show.reset_index(drop=True), use_container_width=True, height=500)
        st.caption(f"Mostrando {len(df_show)} de {len(df_all)} registros.")
        st.markdown("---")
        st.markdown("**🗑️ Eliminar un registro**")
        ec1, ec2 = st.columns(2)
        with ec1:
            st.markdown("**Eliminar el último registro cargado:**")
            if st.button("🗑️ Eliminar último registro"):
                save_data(df_all.iloc[:-1])
                st.success("Último registro eliminado."); st.rerun()
        with ec2:
            st.markdown("**Eliminar registro específico:**")
            if not df_show.empty:
                fila_a_borrar = st.selectbox("Seleccioná el registro",
                    options=list(df_show.index),
                    format_func=lambda i: f"{df_all.loc[i,'Nombre y Apellido']} | {df_all.loc[i,'Fecha']} | {df_all.loc[i,'Movilidad Gremial x Semana x Dia']}")
                if st.button("🗑️ Eliminar registro seleccionado", type="primary"):
                    save_data(df_all.drop(index=fila_a_borrar).reset_index(drop=True))
                    st.success("Registro eliminado."); st.rerun()

        st.markdown("---")
        st.markdown("**✏️ Editar un registro**")
        if not df_show.empty:
            fila_edit = st.selectbox("Seleccioná el registro a editar", options=list(df_show.index),
                format_func=lambda i: f"{df_all.loc[i,'Nombre y Apellido']} | {df_all.loc[i,'Fecha']} | {df_all.loc[i,'Movilidad Gremial x Semana x Dia']}",
                key="sel_edit")
            row = df_all.loc[fila_edit]
            with st.form("form_editar"):
                e1, e2, e3 = st.columns(3)
                with e1:
                    e_nombre = st.text_input("Nombre y Apellido", value=row["Nombre y Apellido"])
                    e_legajo = st.text_input("Legajo", value=row["Legajo"])
                    e_cuerpo = st.text_input("Cuerpo Gremial", value=row["Cuerpo Gremial"])
                with e2:
                    e_sector = st.selectbox("Sector", SECTORES_OPTS, index=SECTORES_OPTS.index(row["Sector"]) if row["Sector"] in SECTORES_OPTS else 0)
                    e_cargo  = st.text_input("Cargo", value=row["Cargo"])
                    e_turno  = st.selectbox("Turno", TURNO_OPTS, index=TURNO_OPTS.index(row["Turno"]) if row["Turno"] in TURNO_OPTS else 0)
                with e3:
                    e_reporta = st.text_input("Reporta a", value=row["Reporta a"])
                    try:    e_fecha = st.date_input("Fecha", value=pd.to_datetime(row["Fecha"], dayfirst=True), format="DD/MM/YYYY")
                    except: e_fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")
                em1, em2 = st.columns(2)
                with em1: e_mov    = st.selectbox("Movilidad Gremial", MOVILIDAD_OPTS, index=MOVILIDAD_OPTS.index(row["Movilidad Gremial x Semana x Dia"]) if row["Movilidad Gremial x Semana x Dia"] in MOVILIDAD_OPTS else 0)
                with em2: e_motexc = st.selectbox("Motivo Excedencia", MOTIVO_EXCEDENCIA_OPTS, index=MOTIVO_EXCEDENCIA_OPTS.index(row["Motivo Excedencia"]) if row["Motivo Excedencia"] in MOTIVO_EXCEDENCIA_OPTS else 0)
                el1, el2, el3 = st.columns(3)
                with el1: e_lic    = st.selectbox("Licencia", LICENCIAS_OPTS, index=LICENCIAS_OPTS.index(row["Licencia"]) if row["Licencia"] in LICENCIAS_OPTS else 0)
                with el2: e_ilic   = st.text_input("Info Licencia", value=row["Informacion Licencia"])
                with el3: e_llt    = st.selectbox("LLT/Ausencia", LLT_OPTS, index=LLT_OPTS.index(row["LLT/Ausencia Inj"]) if row["LLT/Ausencia Inj"] in LLT_OPTS else 0)
                eo1, eo2, eo3 = st.columns(3)
                with eo1: e_obs    = st.text_area("Observaciones", value=row["Observaciones Extras"], height=70)
                with eo2: e_mdes   = st.text_area("Motivo Desvío", value=row["Motivo (Detallar desvios)"], height=70)
                with eo3: e_acc    = st.selectbox("Acción", ACCION_OPTS, index=ACCION_OPTS.index(row["Accion"]) if row["Accion"] in ACCION_OPTS else 0)
                if st.form_submit_button("💾 Guardar cambios", type="primary", use_container_width=True):
                    for col, val in [("Nombre y Apellido",e_nombre),("Legajo",e_legajo),("Cuerpo Gremial",e_cuerpo),
                                     ("Sector",e_sector),("Cargo",e_cargo),("Turno",e_turno),("Reporta a",e_reporta),
                                     ("Fecha",e_fecha.strftime("%d/%m/%Y")),("Movilidad Gremial x Semana x Dia",e_mov),
                                     ("Motivo Excedencia",e_motexc),("Licencia",e_lic),("Informacion Licencia",e_ilic),
                                     ("LLT/Ausencia Inj",e_llt),("Observaciones Extras",e_obs),
                                     ("Motivo (Detallar desvios)",e_mdes),("Accion",e_acc)]:
                        df_all.loc[fila_edit, col] = val
                    save_data(df_all)
                    st.success("✅ Registro actualizado."); st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — EXPORTAR
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "Exportar Excel":
    df_all = load_data(_mtime=_get_mtime(DATA_FILE))
    st.markdown('<div class="section-title">Exportar a Excel</div>', unsafe_allow_html=True)
    if df_all.empty:
        st.info("No hay datos para exportar.")
    else:
        fe1, fe2 = st.columns(2)
        with fe1: exp_desde = st.date_input("Desde", value=date.today()-timedelta(days=30), format="DD/MM/YYYY")
        with fe2: exp_hasta = st.date_input("Hasta", value=date.today(), format="DD/MM/YYYY")
        sel_exp = st.selectbox("Delegado", ["Todos"] + sorted(df_all["Nombre y Apellido"].dropna().unique().tolist()))
        df_exp = df_all.copy()
        df_exp["_fecha"] = _parsear_fechas(df_exp)
        df_exp = df_exp[(df_exp["_fecha"] >= pd.Timestamp(exp_desde)) & (df_exp["_fecha"] <= pd.Timestamp(exp_hasta))]
        if sel_exp != "Todos": df_exp = df_exp[df_exp["Nombre y Apellido"] == sel_exp]
        df_exp = df_exp.drop(columns=["_fecha"])
        st.info(f"Se exportarán **{len(df_exp)} registros**.")
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df_exp.to_excel(w, index=False, sheet_name="Registro Gremial")
            ws = w.sheets["Registro Gremial"]
            for col_cells in ws.columns:
                ws.column_dimensions[col_cells[0].column_letter].width = min(max(len(str(c.value or "")) for c in col_cells)+4, 40)
        buf.seek(0)
        st.download_button("⬇️ Descargar Excel", data=buf,
            file_name=f"registro_gremial_{exp_desde.strftime('%d%m%Y')}_{exp_hasta.strftime('%d%m%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True, type="primary")



# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — DASHBOARD GERENCIAL  ✅ FIX: parseo robusto + período desde la base
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "Dashboard Gerencial":
    df_all = load_data(_mtime=_get_mtime(DATA_FILE))
    if df_all.empty:
        st.info("Aún no hay registros cargados.")
    else:
        df_all["_fecha"] = _parsear_fechas(df_all)
        fechas_validas = df_all["_fecha"].dropna()
        if fechas_validas.empty:
            st.warning("No se pudieron interpretar las fechas. Verificá el formato (dd/mm/aaaa).")
            st.stop()

        fecha_min_data = fechas_validas.min().date()
        fecha_max_data = fechas_validas.max().date()

        # Por defecto: todo el rango disponible (no los últimos 180 días)
        fc1, fc2 = st.columns(2)
        with fc1: d_desde = st.date_input("Desde", value=fecha_min_data, format="DD/MM/YYYY", key="dash_desde")
        with fc2: d_hasta = st.date_input("Hasta", value=fecha_max_data, format="DD/MM/YYYY", key="dash_hasta")

        df_d = df_all[(df_all["_fecha"] >= pd.Timestamp(d_desde)) & (df_all["_fecha"] <= pd.Timestamp(d_hasta))].copy()
        # Matching robusto: strip espacios, comparación case-insensitive
        df_d["_es_desvio"] = df_d["Movilidad Gremial x Semana x Dia"].apply(es_desvio)

        if df_d.empty:
            st.warning(f"Sin datos entre {d_desde.strftime('%d/%m/%Y')} y {d_hasta.strftime('%d/%m/%Y')}. "
                       f"La base tiene registros desde {fecha_min_data.strftime('%d/%m/%Y')} hasta {fecha_max_data.strftime('%d/%m/%Y')}.")
        else:
            tot_dev    = int(df_d["_es_desvio"].sum())
            del_afect  = int(df_d[df_d["_es_desvio"]]["Nombre y Apellido"].nunique())
            reincid    = int((df_d[df_d["_es_desvio"]].groupby("Nombre y Apellido").size() >= 3).sum())
            sector_top = df_d[df_d["_es_desvio"]]["Sector"].value_counts().index[0] if tot_dev > 0 else "—"
            periodo    = f"{d_desde.strftime('%d/%m/%y')} — {d_hasta.strftime('%d/%m/%y')}"

            st.markdown(f"""<div style="background:#1A2C5B;color:white;padding:12px 20px;border-radius:8px;margin-bottom:16px;">
                <b style="font-size:1.1rem">RESUMEN EJECUTIVO — {periodo}</b></div>""", unsafe_allow_html=True)

            k1,k2,k3,k4 = st.columns(4)
            with k1:
                st.markdown(f"""<div style="border-radius:10px;padding:20px;text-align:center;background:#FEE2E2;border-top:4px solid #C0392B;">
                    <div style="font-size:.7rem;color:#666;text-transform:uppercase">Total Desvíos</div>
                    <div style="font-size:2.8rem;font-weight:700;color:#C0392B">{tot_dev}</div>
                    <div style="font-size:.75rem;color:#888">en el período</div></div>""", unsafe_allow_html=True)
            with k2:
                st.markdown(f"""<div style="border-radius:10px;padding:20px;text-align:center;background:#FEF3C7;border-top:4px solid #E67E22;">
                    <div style="font-size:.7rem;color:#666;text-transform:uppercase">Delegados afectados</div>
                    <div style="font-size:2.8rem;font-weight:700;color:#E67E22">{del_afect}</div>
                    <div style="font-size:.75rem;color:#888">con al menos 1 desvío</div></div>""", unsafe_allow_html=True)
            with k3:
                cr = "#C0392B" if reincid>5 else "#E67E22" if reincid>2 else "#27AE60"
                bg = "#FEE2E2" if reincid>5 else "#FEF3C7" if reincid>2 else "#D1FAE5"
                st.markdown(f"""<div style="border-radius:10px;padding:20px;text-align:center;background:{bg};border-top:4px solid {cr};">
                    <div style="font-size:.7rem;color:#666;text-transform:uppercase">Reincidentes</div>
                    <div style="font-size:2.8rem;font-weight:700;color:{cr}">{reincid}</div>
                    <div style="font-size:.75rem;color:#888">3 o más desvíos</div></div>""", unsafe_allow_html=True)
            with k4:
                n_st = int(df_d[df_d["_es_desvio"] & (df_d["Sector"]==sector_top)]["_es_desvio"].sum()) if tot_dev > 0 else 0
                st.markdown(f"""<div style="border-radius:10px;padding:20px;text-align:center;background:#F3E8FF;border-top:4px solid #8E44AD;">
                    <div style="font-size:.7rem;color:#666;text-transform:uppercase">Sector más crítico</div>
                    <div style="font-size:1.3rem;font-weight:700;color:#8E44AD;margin:8px 0">{sector_top}</div>
                    <div style="font-size:.75rem;color:#888">{n_st} desvíos</div></div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            MESES_ES = {"January":"Ene","February":"Feb","March":"Mar","April":"Abr","May":"May","June":"Jun",
                        "July":"Jul","August":"Ago","September":"Sep","October":"Oct","November":"Nov","December":"Dic"}

            df_d["_mes_dt"] = df_d["_fecha"].dt.to_period("M").dt.to_timestamp()
            mes_dev = df_d[df_d["_es_desvio"]].groupby("_mes_dt").size().sort_index()
            total_mes = mes_dev.sum() if not mes_dev.empty else 1
            mes_labeled = mes_dev.copy()
            mes_labeled.index = [f"{MESES_ES.get(d.strftime('%B'),d.strftime('%B'))} {d.strftime('%y')}" for d in mes_dev.index]
            mes_pct = (mes_labeled / total_mes * 100).round(1)

            sector_dev    = df_d[df_d["_es_desvio"]].groupby("Sector").size().sort_values(ascending=False).head(5)
            total_sec_dev = sector_dev.sum() if not sector_dev.empty else 1

            col_izq, col_der = st.columns(2)
            with col_izq:
                st.markdown("""<div style="background:#1A2C5B;color:white;padding:10px 16px;border-radius:8px;margin-bottom:12px;">
                    <b>📅 TENDENCIA MENSUAL</b></div>""", unsafe_allow_html=True)
                if mes_labeled.empty:
                    st.info("Sin desvíos en el período.")
                else:
                    st.bar_chart(mes_labeled.rename("Desvíos"), color="#C0392B")
                    cols_mes = st.columns(min(len(mes_labeled), 4))
                    for i, (mes, n) in enumerate(mes_labeled.items()):
                        pct_m = mes_pct[mes]
                        cm = "#C0392B" if pct_m >= 30 else "#E67E22" if pct_m >= 20 else "#27AE60"
                        with cols_mes[i % 4]:
                            st.markdown(f"""<div style="text-align:center;padding:6px;border-top:3px solid {cm};background:#f9f9f9;border-radius:4px;margin-bottom:4px;">
                                <div style="font-size:.72rem;color:#666">{mes}</div>
                                <div style="font-weight:700;color:{cm}">{int(n)} dev.</div>
                                <div style="font-size:.75rem;color:{cm}">{pct_m}%</div>
                            </div>""", unsafe_allow_html=True)
                    st.caption("📌 % = desvíos del mes sobre el total del período")

            with col_der:
                st.markdown("""<div style="background:#1A2C5B;color:white;padding:10px 16px;border-radius:8px;margin-bottom:12px;">
                    <b>🏭 TOP SECTORES</b></div>""", unsafe_allow_html=True)
                if sector_dev.empty:
                    st.info("Sin desvíos por sector.")
                else:
                    for sec, n in sector_dev.items():
                        pct_s = round(n / total_sec_dev * 100, 1)
                        cs = "#C0392B" if pct_s >= 25 else "#E67E22" if pct_s >= 15 else "#F39C12"
                        st.markdown(f"""<div style="margin-bottom:12px;">
                            <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                                <span style="font-size:.85rem;font-weight:600">{sec}</span>
                                <span style="font-size:.85rem;font-weight:700;color:{cs}">{int(n)} dev. — {pct_s}%</span>
                            </div>
                            <div style="background:#eee;border-radius:4px;height:10px;">
                                <div style="background:{cs};width:{pct_s}%;height:10px;border-radius:4px"></div>
                            </div></div>""", unsafe_allow_html=True)
                    st.caption("📌 % sobre el total de desvíos del período")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""<div style="background:#1A2C5B;color:white;padding:10px 16px;border-radius:8px;margin-bottom:12px;">
                <b>🚨 TOP 5 DELEGADOS CON MÁS DESVÍOS</b></div>""", unsafe_allow_html=True)

            del_dev   = df_d[df_d["_es_desvio"]].groupby("Nombre y Apellido").size().sort_values(ascending=False).head(5)
            del_sector = df_d.groupby("Nombre y Apellido")["Sector"].first()
            del_turno  = df_d.groupby("Nombre y Apellido")["Turno"].first()
            del_super  = df_d.groupby("Nombre y Apellido")["Reporta a"].first()
            colors_rank = ["#C0392B","#8E44AD","#E67E22","#2980B9","#27AE60"]

            if del_dev.empty:
                st.info("Sin desvíos en el período.")
            else:
                for i, (nom, n_dev) in enumerate(del_dev.items()):
                    tipos  = df_d[(df_d["Nombre y Apellido"]==nom) & df_d["_es_desvio"]]["Movilidad Gremial x Semana x Dia"].value_counts()
                    tipo_p = tipos.index[0] if not tipos.empty else ""
                    ct = colors_rank[i]
                    st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;padding:12px;margin-bottom:8px;border:1px solid #eee;border-radius:8px;">
                        <div style="background:{ct};color:white;font-weight:700;font-size:1.1rem;padding:10px 14px;border-radius:6px;min-width:42px;text-align:center">#{i+1}</div>
                        <div style="flex:1">
                            <div style="font-weight:700;font-size:.95rem">{nom}</div>
                            <div style="color:#666;font-size:.8rem">{del_sector.get(nom,"")} · Turno {del_turno.get(nom,"")} · Sup: {del_super.get(nom,"")}</div>
                            <div style="color:#999;font-size:.78rem;margin-top:2px">Principal: {tipo_p}</div>
                        </div>
                        <div style="background:{ct};color:white;font-weight:700;padding:8px 16px;border-radius:6px;text-align:center;min-width:80px;font-size:1.1rem">{n_dev} dev.</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("---")
            try:
                buf_ger = io.BytesIO()
                with pd.ExcelWriter(buf_ger, engine="openpyxl") as w:
                    pd.DataFrame({"Métrica":["Total Desvíos","Delegados Afectados","Reincidentes (≥3)","Sector más crítico"],
                                  "Valor":[tot_dev,del_afect,reincid,sector_top]}).to_excel(w, index=False, sheet_name="Resumen")
                    if not sector_dev.empty:
                        sector_dev.reset_index().rename(columns={0:"Desvíos"}).to_excel(w, index=False, sheet_name="Por Sector")
                    if not del_dev.empty:
                        del_dev.reset_index().rename(columns={0:"Desvíos","Nombre y Apellido":"Delegado"}).to_excel(w, index=False, sheet_name="Top Delegados")
                    if not mes_labeled.empty:
                        mes_labeled.reset_index().rename(columns={0:"Desvíos","index":"Mes"}).to_excel(w, index=False, sheet_name="Tendencia Mensual")
                buf_ger.seek(0)
                st.download_button("⬇️ Exportar Dashboard a Excel", data=buf_ger,
                    file_name=f"dashboard_{d_desde.strftime('%d%m%Y')}_{d_hasta.strftime('%d%m%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, type="primary")
            except Exception as e:
                st.warning(f"No se pudo generar el Excel: {e}")



# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — IMPORTAR HISTÓRICO
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "Importar Historico":
    st.markdown('<div class="section-title">Importar Histórico desde Excel</div>', unsafe_allow_html=True)
    st.info("Subí el Excel de Analisis.xlsx (solapa Datos) o cualquier Excel de registro semanal.")

    tipo_import = st.radio(
        "Tipo de archivo a importar",
        [
            "Excel de Analisis (solapa Datos — historico Nov a Marzo)",
            "Excel Bloque Gremial (una solapa por semana — Abril en adelante)",
            "Excel de registro gremial (formato estandar)"
        ],
        key="tipo_import"
    )

    archivo = st.file_uploader("Selecciona tu archivo Excel (.xlsx)", type=["xlsx","xls"])

    # ── Opción 1: Excel de Analisis (historico Nov-Marzo) ──
    if archivo and "Analisis" in tipo_import:
        try:
            from importar_analisis import convertir_analisis_a_registro
            df_conv = convertir_analisis_a_registro(archivo)
            n_dev = (df_conv['Movilidad Gremial x Semana x Dia']!='Cumple').sum()
            n_cum = (df_conv['Movilidad Gremial x Semana x Dia']=='Cumple').sum()
            st.success(f"Archivo procesado: **{len(df_conv)} registros** — {n_dev} desvios, {n_cum} cumple ({round(n_dev/len(df_conv)*100,1)}% tasa)")
            st.dataframe(df_conv[df_conv['Movilidad Gremial x Semana x Dia']!='Cumple'].head(20), use_container_width=True)
            if st.button("Confirmar importacion del Analisis.xlsx", type="primary", use_container_width=True):
                df_actual = load_data(_mtime=_get_mtime(DATA_FILE))
                df_combinado = pd.concat([df_conv, df_actual], ignore_index=True)
                df_combinado = df_combinado.drop_duplicates(
                    subset=["Legajo","Fecha","Movilidad Gremial x Semana x Dia"], keep="last"
                )
                save_data(df_combinado)
                st.success(f"Importacion exitosa — {len(df_combinado)} registros totales.")
                st.balloons()
        except ImportError:
            st.error("No se encontro importar_analisis.py. Asegurate de que esté en la misma carpeta que app.py.")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
        st.stop()

    # ── Opción 2: Excel Bloque Gremial (Abril en adelante) ──
    if archivo and "Bloque Gremial" in tipo_import:
        try:
            from importar_bloque import convertir_bloque_a_registro, MESES_DESDE_ABRIL

            meses_sel = st.multiselect(
                "Meses a importar",
                MESES_DESDE_ABRIL,
                default=MESES_DESDE_ABRIL,
                key="meses_bloque"
            )

            if meses_sel:
                df_conv2, solapas_proc = convertir_bloque_a_registro(archivo, meses_incluir=meses_sel)
                if df_conv2.empty:
                    st.warning("No se encontraron registros en las solapas seleccionadas.")
                else:
                    n_dev2 = (~df_conv2['Movilidad Gremial x Semana x Dia'].str.lower().isin(['cumple',''])).sum()
                    n_cum2 = len(df_conv2) - n_dev2
                    st.success(f"Solapas procesadas: {len(solapas_proc)} — **{len(df_conv2)} registros** — {n_dev2} desvios, {n_cum2} cumple ({round(n_dev2/len(df_conv2)*100,1)}% tasa)")
                    with st.expander("Ver solapas procesadas"):
                        st.write(solapas_proc)
                    st.dataframe(
                        df_conv2[~df_conv2['Movilidad Gremial x Semana x Dia'].str.lower().isin(['cumple',''])].head(20),
                        use_container_width=True
                    )
                    if st.button("Confirmar importacion del Bloque Gremial", type="primary", use_container_width=True):
                        df_actual2 = load_data(_mtime=_get_mtime(DATA_FILE))
                        df_combinado2 = pd.concat([df_conv2, df_actual2], ignore_index=True)
                        df_combinado2 = df_combinado2.drop_duplicates(
                            subset=["Legajo","Fecha","Movilidad Gremial x Semana x Dia"], keep="last"
                        )
                        save_data(df_combinado2)
                        st.success(f"Importacion exitosa — {len(df_combinado2)} registros totales.")
                        st.balloons()
        except ImportError:
            st.error("No se encontro importar_bloque.py. Asegurate de que esté en la misma carpeta que app.py.")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
        st.stop()
    if archivo:
        try:
            import re as _re
            xl = pd.ExcelFile(archivo)
            st.success(f"Archivo cargado: **{len(xl.sheet_names)} solapas** encontradas.")

            def _fecha_de_solapa(nombre):
                m = _re.search(r'(\d{1,2})[/\-\.](\d{1,2})', nombre)
                if m:
                    dia, mes = m.group(1), m.group(2)
                    anio = "2025" if int(mes) >= 10 else "2026"
                    try: return f"{dia.zfill(2)}/{mes.zfill(2)}/{anio}"
                    except: pass
                return ""

            dfs, errores = [], []
            for hoja in xl.sheet_names:
                try:
                    # Solapa DATOS del Analisis.xlsx — formato especial con columnas conocidas
                    if hoja.strip().lower() == "datos":
                        df_raw_check = xl.parse(hoja, header=None, dtype=str, nrows=3)
                        row_vals_all = [str(v).lower() for row in df_raw_check.values for v in row if pd.notna(v)]
                        if not any("legajo" in v or "nombre" in v for v in row_vals_all):
                            continue  # Solapa sin datos de delegados

                    df_raw = xl.parse(hoja, header=None, dtype=str)
                    header_row = 0
                    for i in range(min(5, len(df_raw))):
                        row_vals = [str(v).lower() for v in df_raw.iloc[i].values if pd.notna(v)]
                        if any("legajo" in v or "nombre" in v for v in row_vals):
                            header_row = i; break
                    df_h = xl.parse(hoja, header=header_row, dtype=str).dropna(how="all")
                    col_map = {}
                    for c in df_h.columns:
                        cl = str(c).lower().strip()
                        if "legajo" in cl:                               col_map[c] = "Legajo"
                        elif "nombre" in cl and "apellido" in cl:        col_map[c] = "Nombre y Apellido"
                        elif "cuerpo" in cl:                             col_map[c] = "Cuerpo Gremial"
                        elif "sector" in cl:                             col_map[c] = "Sector"
                        elif "cargo" in cl:                              col_map[c] = "Cargo"
                        elif "turno" in cl:                              col_map[c] = "Turno"
                        elif "reporta" in cl:                            col_map[c] = "Reporta a"
                        elif "fecha" in cl:                              col_map[c] = "Fecha"
                        elif "movilidad" in cl:                         col_map[c] = "Movilidad Gremial x Semana x Dia"
                        elif "motivo" in cl and "excedencia" in cl:     col_map[c] = "Motivo Excedencia"
                        elif "motivo" in cl and "licencia" in cl:       col_map[c] = "Informacion Licencia"
                        elif "licencia" in cl:                           col_map[c] = "Licencia"
                        elif "llt" in cl or "ausencia" in cl:           col_map[c] = "LLT/Ausencia Inj"
                        elif "observ" in cl:                             col_map[c] = "Observaciones Extras"
                        elif "motivo" in cl and "desv" in cl:           col_map[c] = "Motivo (Detallar desvios)"
                        elif "accion" in cl or "acción" in cl:          col_map[c] = "Accion"
                    df_h = df_h.rename(columns=col_map).loc[:, ~df_h.rename(columns=col_map).columns.duplicated()]
                    if "Fecha" not in df_h.columns or df_h["Fecha"].isna().all() or (df_h["Fecha"].astype(str).str.strip()=="").all():
                        df_h["Fecha"] = _fecha_de_solapa(hoja)
                    for col in COLUMNS:
                        if col not in df_h.columns: df_h[col] = ""
                    df_h = df_h[COLUMNS]
                    df_h = df_h[df_h["Nombre y Apellido"].notna() &
                                (df_h["Nombre y Apellido"].str.strip() != "") &
                                (df_h["Nombre y Apellido"].str.lower().str.strip() != "nombre y apellido")]
                    df_h = df_h[df_h["Legajo"].notna() & (df_h["Legajo"].str.strip() != "")]
                    if not df_h.empty: dfs.append(df_h)
                except Exception as e:
                    errores.append(f"Solapa '{hoja}': {e}")

            for e in errores: st.warning(f"⚠️ {e}")
            if dfs:
                df_hist = pd.concat(dfs, ignore_index=True).fillna("")
                st.markdown(f"**Vista previa — {len(df_hist)} registros en {len(dfs)} solapas:**")
                st.dataframe(df_hist.head(30), use_container_width=True)
                if st.button("✅ Confirmar importación", type="primary", use_container_width=True):
                    df_actual = load_data(_mtime=_get_mtime(DATA_FILE))
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
elif pagina == "Presencia del Dia":
    st.markdown('<div class="section-title">Presencia del Día</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1: fecha_sel = st.date_input("📅 Fecha", value=date.today(), format="DD/MM/YYYY", key="fecha_presencia")
    with f2: fil_turno = st.selectbox("Turno", ["Todos","BLANCO","NARANJA","AMARILLO","ROT2","ROT4"], key="fp_turno")
    with f3: fil_cargo = st.selectbox("Cargo", ["Todos","CIR","Delegado"], key="fp_cargo")
    with f4: fil_sec   = st.selectbox("Sector", ["Todos"]+SECTORES_OPTS, key="fp_sector")

    fecha_str = fecha_sel.strftime("%d/%m/%Y")
    df_pres   = load_presencia()
    df_hoy    = df_pres[df_pres["Fecha"] == fecha_str].copy() if not df_pres.empty else pd.DataFrame()

    lista_base = []
    for leg, d in DELEGADOS.items():
        est, obs = "Presente", ""
        if not df_hoy.empty:
            fila = df_hoy[df_hoy["Legajo"] == leg]
            if not fila.empty:
                est = fila.iloc[0]["Estado"]
                obs = str(fila.iloc[0].get("Observacion",""))
        lista_base.append({"Legajo":leg,"Nombre y Apellido":d["nombre"],"Sector":d["sector"],
                           "Turno":d["turno"],"Cargo":d["cargo"],"Estado":est,"Observacion":obs})
    df_base = pd.DataFrame(lista_base)

    df_fil = df_base.copy()
    if fil_turno != "Todos": df_fil = df_fil[df_fil["Turno"]==fil_turno]
    if fil_cargo != "Todos": df_fil = df_fil[df_fil["Cargo"]==fil_cargo]
    if fil_sec   != "Todos": df_fil = df_fil[df_fil["Sector"]==fil_sec]

    st.markdown("**📂 Cargar fichadas WD (opcional)**")
    fichadas_file = st.file_uploader("Subí el Excel de fichadas del día", type=["xlsx","xls"], key="fichadas_wd")
    if fichadas_file:
        try:
            df_fich = pd.read_excel(fichadas_file, dtype=str)
            col_leg_f = next((c for c in df_fich.columns if "legajo" in str(c).lower()), None)
            if col_leg_f:
                df_fc = df_fich[df_fich[col_leg_f].notna()].copy()
                df_fc = df_fc[df_fc[col_leg_f].str.strip().str.match(r"^[0-9]+$")]
                col_hora = next((c for c in df_fc.columns if "entrada" in str(c).lower().replace(" ","") or
                    ("hora" in str(c).lower() and "salida" not in str(c).lower())), None)
                df_pres_fich = df_fc if col_hora is None else df_fc[df_fc[col_hora].notna() & (df_fc[col_hora].astype(str).str.strip().isin(["","nan"])==False)]
                legs_pres = set(df_pres_fich[col_leg_f].str.strip().tolist())
                df_base["Estado"] = df_base["Legajo"].apply(lambda l: "Presente" if str(l).strip() in legs_pres else "Pendiente")
                df_fil = df_base.copy()
                if fil_turno != "Todos": df_fil = df_fil[df_fil["Turno"]==fil_turno]
                if fil_cargo != "Todos": df_fil = df_fil[df_fil["Cargo"]==fil_cargo]
                if fil_sec   != "Todos": df_fil = df_fil[df_fil["Sector"]==fil_sec]
                pres_n = (df_base["Estado"]=="Presente").sum()
                pend_n = (df_base["Estado"]=="Pendiente").sum()
                st.success(f"✅ Fichadas procesadas — **{pres_n} presentes**, **{pend_n} pendientes**.")
            else:
                st.error("No se encontró columna Legajo en el archivo.")
        except Exception as e:
            st.error(f"Error al leer fichadas: {e}")

    st.caption(f"Mostrando {len(df_fil)} delegados para el {fecha_str}")

    nuevos = []
    df_pres_f  = df_fil[df_fil["Estado"]=="Presente"].sort_values(["Turno","Nombre y Apellido"])
    df_pend_f  = df_fil[df_fil["Estado"]=="Pendiente"].sort_values(["Turno","Nombre y Apellido"])
    df_ause_f  = df_fil[df_fil["Estado"].isin(["Ausente","Licencia","Vacaciones"])].sort_values(["Turno","Nombre y Apellido"])

    def _fila_presencia(row, default_idx=0):
        c1,c2,c3,c4,c5,c6 = st.columns([3,2,1,1,2,2])
        c1.write(row["Nombre y Apellido"]); c2.write(row["Sector"]); c3.write(row["Turno"]); c4.write(row["Cargo"])
        ei = ESTADOS_PRESENCIA.index(row["Estado"]) if row["Estado"] in ESTADOS_PRESENCIA else default_idx
        est = c5.selectbox("", ESTADOS_PRESENCIA, index=ei, key=f"est_{row['Legajo']}", label_visibility="collapsed")
        obs = c6.text_input("", value=row["Observacion"], key=f"obs_{row['Legajo']}", placeholder="Observación", label_visibility="collapsed")
        return {"Legajo":row["Legajo"],"Nombre y Apellido":row["Nombre y Apellido"],"Sector":row["Sector"],
                "Turno":row["Turno"],"Cargo":row["Cargo"],"Fecha":fecha_str,"Estado":est,"Observacion":obs}

    with st.form("form_presencia"):
        if not df_pres_f.empty:
            st.markdown("**✅ Con fichada — Presentes**")
            h1,h2,h3,h4,h5,h6 = st.columns([3,2,1,1,2,2])
            for hx,lbl in zip([h1,h2,h3,h4,h5,h6],["**Nombre**","**Sector**","**Turno**","**Cargo**","**Estado**","**Observación**"]): hx.markdown(lbl)
            st.divider()
            for _, row in df_pres_f.iterrows(): nuevos.append(_fila_presencia(row, 0))
        st.markdown("---")
        if not df_pend_f.empty:
            st.markdown(f"**🕐 Pendiente de fichar — {len(df_pend_f)} delegados**")
            h1,h2,h3,h4,h5,h6 = st.columns([3,2,1,1,2,2])
            for hx,lbl in zip([h1,h2,h3,h4,h5,h6],["**Nombre**","**Sector**","**Turno**","**Cargo**","**Estado**","**Observación**"]): hx.markdown(lbl)
            st.divider()
            for _, row in df_pend_f.iterrows(): nuevos.append(_fila_presencia(row, 1))
        st.markdown("---")
        if not df_ause_f.empty:
            st.markdown(f"**⚠️ Sin fichada — {len(df_ause_f)} delegados**")
            h1,h2,h3,h4,h5,h6 = st.columns([3,2,1,1,2,2])
            for hx,lbl in zip([h1,h2,h3,h4,h5,h6],["**Nombre**","**Sector**","**Turno**","**Cargo**","**Estado**","**Observación**"]): hx.markdown(lbl)
            st.divider()
            for _, row in df_ause_f.iterrows(): nuevos.append(_fila_presencia(row, 0))

        if st.form_submit_button("💾 Guardar Presencia", type="primary", use_container_width=True):
            completa = []
            for leg, d in DELEGADOS.items():
                match = next((r for r in nuevos if r["Legajo"]==leg), None)
                if match:
                    completa.append(match)
                elif not df_hoy.empty:
                    f = df_hoy[df_hoy["Legajo"]==leg]
                    completa.append(f.iloc[0].to_dict() if not f.empty else
                        {"Legajo":leg,"Nombre y Apellido":d["nombre"],"Sector":d["sector"],"Turno":d["turno"],
                         "Cargo":d["cargo"],"Fecha":fecha_str,"Estado":"Presente","Observacion":""})
                else:
                    completa.append({"Legajo":leg,"Nombre y Apellido":d["nombre"],"Sector":d["sector"],"Turno":d["turno"],
                         "Cargo":d["cargo"],"Fecha":fecha_str,"Estado":"Presente","Observacion":""})
            df_full = pd.DataFrame(completa)
            if not df_pres.empty: df_pres = df_pres[df_pres["Fecha"]!=fecha_str]
            df_pres = pd.concat([df_pres, df_full], ignore_index=True)
            save_presencia(df_pres)
            st.success(f"✅ Presencia del {fecha_str} guardada.")
            st.rerun()

    st.markdown("---")
    if not df_hoy.empty:
        r1,r2,r3,r4,r5 = st.columns(5)
        r1.markdown(f'<div class="kpi-card ok"><div class="kpi-label">Presentes</div><div class="kpi-value">{(df_hoy["Estado"]=="Presente").sum()}</div></div>', unsafe_allow_html=True)
        r2.markdown(f'<div class="kpi-card"><div class="kpi-label">Pendientes</div><div class="kpi-value">{(df_hoy["Estado"]=="Pendiente").sum()}</div></div>', unsafe_allow_html=True)
        r3.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Ausentes</div><div class="kpi-value">{(df_hoy["Estado"]=="Ausente").sum()}</div></div>', unsafe_allow_html=True)
        r4.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Licencia</div><div class="kpi-value">{(df_hoy["Estado"]=="Licencia").sum()}</div></div>', unsafe_allow_html=True)
        r5.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Vacaciones</div><div class="kpi-value">{(df_hoy["Estado"]=="Vacaciones").sum()}</div></div>', unsafe_allow_html=True)
        df_np = df_hoy[df_hoy["Estado"]!="Presente"]
        if not df_np.empty:
            st.markdown("**⚠️ No presentes:**")
            st.dataframe(df_np[["Nombre y Apellido","Turno","Sector","Cargo","Estado","Observacion"]].reset_index(drop=True), use_container_width=True)
    else:
        st.info("Guardá la presencia para ver el resumen.")



# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — PADRÓN DELEGADOS  (con historial de altas/bajas)
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "Padron Delegados":
    st.markdown('<div class="section-title">Padrón de Delegados y CIR — SMATA Planta</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Padrón Actual", "➕ Alta / Baja", "📜 Historial de Movimientos"])
    df_pad = load_padron()

    with tab1:
        df_act = df_pad[df_pad["Activo"]=="Sí"]
        k1,k2,k3,k4 = st.columns(4)
        k1.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Representantes</div><div class="kpi-value">{len(df_act)}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi-card ok"><div class="kpi-label">Delegados</div><div class="kpi-value">{(df_act["Cargo"]=="Delegado").sum()}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi-card warning"><div class="kpi-label">CIR</div><div class="kpi-value">{(df_act["Cargo"]=="CIR").sum()}</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi-card"><div class="kpi-label">Cuerpos Gremiales</div><div class="kpi-value">{df_act["Cuerpo Gremial"].nunique()}</div></div>', unsafe_allow_html=True)
        # Mandato vigente
        m_info = MANDATOS.get("SMATA Planta", {})
        if m_info.get("inicio"):
            st.markdown(f"""<div style="background:#EEF2FF;border:1px solid #2E4A9E;border-radius:8px;padding:10px 16px;margin:10px 0;display:flex;gap:24px;align-items:center;">
                <div><span style="font-size:.75rem;color:#666;text-transform:uppercase">Mandato vigente</span><br>
                <span style="font-weight:700;color:#2E4A9E">{m_info['periodo']}</span></div>
                <div><span style="font-size:.75rem;color:#666">Inicio</span><br>
                <span style="font-weight:600">{m_info['inicio']}</span></div>
                <div><span style="font-size:.75rem;color:#666">Fin estimado</span><br>
                <span style="font-weight:600">{m_info['fin_estimado']}</span></div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Por Cuerpo Gremial**")
        res_cuerpo = df_act.groupby("Cuerpo Gremial").agg(
            Total=("Legajo","count"), Delegados=("Cargo",lambda x:(x=="Delegado").sum()), CIR=("Cargo",lambda x:(x=="CIR").sum())
        ).reset_index().sort_values("Total", ascending=False)
        hc_total = len(df_act)
        for _, row in res_cuerpo.iterrows():
            pct_hc = round(int(row['Total']) / hc_total * 100, 1) if hc_total > 0 else 0
            st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 16px;margin-bottom:6px;background:#f9f9f9;border-radius:8px;border-left:4px solid #2E4A9E;">
                <span style="font-weight:600">{row['Cuerpo Gremial']}</span>
                <div style="display:flex;gap:16px;">
                    <span style="color:#1A2C5B;font-weight:600">{int(row['Total'])} ({pct_hc}% del HC)</span>
                    <span style="color:#27AE60;font-weight:600">{int(row['Delegados'])} delegados</span>
                    <span style="color:#E67E22;font-weight:600">{int(row['CIR'])} CIR</span>
                </div></div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Por Turno**")
        res_turno = df_act.groupby("Turno").agg(
            Total=("Legajo","count"), Delegados=("Cargo",lambda x:(x=="Delegado").sum()), CIR=("Cargo",lambda x:(x=="CIR").sum())
        ).reset_index().sort_values("Total", ascending=False)
        t_cols = st.columns(max(len(res_turno),1))
        for i, (_, row) in enumerate(res_turno.iterrows()):
            with t_cols[i]:
                st.markdown(f"""<div style="text-align:center;padding:12px;border:1px solid #eee;border-radius:8px;">
                    <div style="font-weight:700;color:#1A2C5B">{row['Turno']}</div>
                    <div style="font-size:1.5rem;font-weight:700">{int(row['Total'])}</div>
                    <div style="font-size:.8rem;color:#27AE60">{int(row['Delegados'])} del.</div>
                    <div style="font-size:.8rem;color:#E67E22">{int(row['CIR'])} CIR</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("---")
        fc1,fc2,fc3 = st.columns(3)
        with fc1: fil_cb  = st.selectbox("Cuerpo Gremial", ["Todos"]+sorted(df_act["Cuerpo Gremial"].unique().tolist()), key="pad_cb")
        with fc2: fil_cg  = st.selectbox("Cargo", ["Todos","Delegado","CIR"], key="pad_cg")
        with fc3: fil_tn  = st.selectbox("Turno", ["Todos"]+sorted(df_act["Turno"].unique().tolist()), key="pad_tn")
        df_sp = df_act.copy()
        if fil_cb != "Todos": df_sp = df_sp[df_sp["Cuerpo Gremial"]==fil_cb]
        if fil_cg != "Todos": df_sp = df_sp[df_sp["Cargo"]==fil_cg]
        if fil_tn != "Todos": df_sp = df_sp[df_sp["Turno"]==fil_tn]
        st.dataframe(df_sp[["Legajo","Nombre y Apellido","Cuerpo Gremial","Sector","Cargo","Turno","Reporta a","Fecha Alta"]].sort_values(["Cuerpo Gremial","Nombre y Apellido"]).reset_index(drop=True), use_container_width=True, height=400)
        st.caption(f"Mostrando {len(df_sp)} de {len(df_act)} representantes activos")

    with tab2:
        st.markdown("### ➕ Registrar Alta de Delegado")
        with st.form("form_alta_smata"):
            a1,a2,a3 = st.columns(3)
            with a1:
                a_leg = st.text_input("Legajo *"); a_nom = st.text_input("Nombre y Apellido *")
                a_cb  = st.selectbox("Cuerpo Gremial", sorted(set(d["cuerpo"] for d in DELEGADOS.values())))
            with a2:
                a_sec = st.selectbox("Sector", SECTORES_OPTS)
                a_car = st.selectbox("Cargo", ["Delegado","CIR"])
                a_tur = st.selectbox("Turno", TURNO_OPTS)
            with a3:
                a_rep = st.text_input("Reporta a")
                a_fec = st.date_input("Fecha Alta *", value=date.today(), format="DD/MM/YYYY")
            if st.form_submit_button("✅ Registrar Alta", type="primary", use_container_width=True):
                if not a_leg or not a_nom:
                    st.error("Completá Legajo y Nombre.")
                else:
                    nueva = {"Legajo":a_leg.strip(),"Nombre y Apellido":a_nom.strip(),"Cuerpo Gremial":a_cb,
                        "Sector":a_sec,"Cargo":a_car,"Turno":a_tur,"Reporta a":a_rep,
                        "Fecha Alta":a_fec.strftime("%d/%m/%Y"),"Fecha Baja":"","Motivo Baja":"","Activo":"Sí"}
                    df_pad = pd.concat([df_pad, pd.DataFrame([nueva])], ignore_index=True)
                    save_padron(df_pad)
                    st.success(f"✅ Alta registrada: {a_nom}"); st.rerun()

        st.markdown("---")
        st.markdown("### 🔴 Registrar Baja de Delegado")
        df_act2 = df_pad[df_pad["Activo"]=="Sí"]
        if df_act2.empty:
            st.info("No hay delegados activos.")
        else:
            sel_baja = st.selectbox("Seleccioná el delegado a dar de baja",
                (df_act2["Legajo"]+" · "+df_act2["Nombre y Apellido"]).tolist())
            leg_baja = sel_baja.split(" · ")[0]
            with st.form("form_baja_smata"):
                b1,b2 = st.columns(2)
                with b1: fb = st.date_input("Fecha de Baja *", value=date.today(), format="DD/MM/YYYY")
                with b2: mb = st.text_input("Motivo de Baja *")
                if st.form_submit_button("🔴 Confirmar Baja", type="primary", use_container_width=True):
                    if not mb:
                        st.error("Ingresá el motivo.")
                    else:
                        idx = df_pad[df_pad["Legajo"]==leg_baja].index
                        df_pad.loc[idx,"Fecha Baja"] = fb.strftime("%d/%m/%Y")
                        df_pad.loc[idx,"Motivo Baja"] = mb
                        df_pad.loc[idx,"Activo"] = "No"
                        save_padron(df_pad)
                        st.success(f"🔴 Baja registrada: {df_pad.loc[idx,'Nombre y Apellido'].iloc[0]}"); st.rerun()

    with tab3:
        st.markdown("### 📜 Historial completo")
        hf1,hf2 = st.columns(2)
        with hf1: fil_est_h = st.selectbox("Estado", ["Todos","Activos","Dados de baja"])
        with hf2: bus_h = st.text_input("Buscar por nombre o legajo")
        df_hsh = df_pad.copy()
        if fil_est_h == "Activos":          df_hsh = df_hsh[df_hsh["Activo"]=="Sí"]
        elif fil_est_h == "Dados de baja":  df_hsh = df_hsh[df_hsh["Activo"]=="No"]
        if bus_h:
            df_hsh = df_hsh[df_hsh["Nombre y Apellido"].str.contains(bus_h,case=False,na=False)|df_hsh["Legajo"].str.contains(bus_h,case=False,na=False)]
        st.dataframe(df_hsh.reset_index(drop=True), use_container_width=True, height=400)
        st.caption(f"{len(df_hsh)} movimientos")
        buf_pad = io.BytesIO()
        with pd.ExcelWriter(buf_pad, engine="openpyxl") as w:
            df_pad.to_excel(w, index=False, sheet_name="Padrón Completo")
            df_pad[df_pad["Activo"]=="Sí"].to_excel(w, index=False, sheet_name="Activos")
            df_pad[df_pad["Activo"]=="No"].to_excel(w, index=False, sheet_name="Bajas")
        buf_pad.seek(0)
        st.download_button("⬇️ Exportar Padrón", data=buf_pad, file_name="padron_delegados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — SMATA FUERA DE PLANTA
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "SMATA Fuera de Planta":
    st.markdown('<div class="section-title">SMATA — Delegados Fuera de Planta / Fuera de TASA</div>', unsafe_allow_html=True)
    df_fdp = _load_fdp()

    # ── KPIs ──
    activos_fdp   = df_fdp[df_fdp["status"] == "Activo"]
    desvincul_fdp = df_fdp[df_fdp["status"] == "Desvinculado"]
    reinc_fdp     = df_fdp[df_fdp["status"] == "Reincorporado a TASA"]
    politic_fdp   = df_fdp[df_fdp["status"] == "Cargo Político"]

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Histórico</div><div class="kpi-value">{len(df_fdp)}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card ok"><div class="kpi-label">Activos Hoy</div><div class="kpi-value">{len(activos_fdp)}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Desvinculados</div><div class="kpi-value">{len(desvincul_fdp)}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Reincorp. a TASA</div><div class="kpi-value">{len(reinc_fdp)}</div></div>', unsafe_allow_html=True)
    k5.markdown(f'<div class="kpi-card warning"><div class="kpi-label">Cargo Político</div><div class="kpi-value">{len(politic_fdp)}</div></div>', unsafe_allow_html=True)

    tab_act, tab_hist, tab_edit = st.tabs(["✅ Activos Hoy", "📜 Historial Completo", "✏️ Editar Padrón"])

    STATUS_COLORS = {
        "Activo":               ("#27AE60", "#D5F0E0"),
        "Desvinculado":         ("#C0392B", "#FCE4E4"),
        "Reincorporado a TASA": ("#E67E22", "#FEF0D5"),
        "Cargo Político":       ("#8E44AD", "#F3E8FF"),
        "Fallecimiento":        ("#4A4A4A", "#EBEBEB"),
        "Renuncia Sindicato":   ("#7F8C8D", "#ECF0F1"),
    }

    with tab_act:
        st.markdown(f"**{len(activos_fdp)} personas actualmente fuera de planta cumpliendo funciones gremiales**")
        st.markdown("")
        for _, row in activos_fdp.sort_values("desde").iterrows():
            color, bg = STATUS_COLORS.get(row["status"], ("#2E4A9E", "#EEF2FF"))
            detalle_txt = f" — {row['detalle']}" if str(row.get("detalle","")).strip() else ""
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;padding:12px 16px;margin-bottom:8px;border:1px solid #eee;border-radius:10px;background:#fafafa;">
                <div style="background:{color};color:white;font-weight:700;padding:8px 12px;border-radius:6px;font-size:1rem;min-width:68px;text-align:center">Leg.<br>{row['legajo']}</div>
                <div style="flex:1">
                    <div style="font-weight:700;font-size:.95rem">{row['nombre']}</div>
                    <div style="color:#444;font-size:.85rem">{row['cargo_gremial']}</div>
                    <div style="color:#888;font-size:.78rem;margin-top:2px">Desde: {row['desde']}{detalle_txt}</div>
                </div>
                <span style="background:{bg};color:{color};padding:4px 12px;border-radius:20px;font-size:.82rem;font-weight:600;white-space:nowrap">{row['status']}</span>
            </div>""", unsafe_allow_html=True)

    with tab_hist:
        st.markdown(f"**{len(df_fdp)} personas con funciones fuera de TASA desde 2008**")
        fil_st = st.selectbox("Filtrar por Status", ["Todos","Activo","Desvinculado","Reincorporado a TASA","Cargo Político"], key="fdp_fil_st")
        df_fdp_show = df_fdp if fil_st == "Todos" else df_fdp[df_fdp["status"] == fil_st]
        df_fdp_show = df_fdp_show.sort_values("desde")
        for _, row in df_fdp_show.iterrows():
            color, bg = STATUS_COLORS.get(row["status"], ("#2E4A9E", "#EEF2FF"))
            detalle_txt = f" — {row['detalle']}" if str(row.get("detalle","")).strip() else ""
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;padding:10px 16px;margin-bottom:6px;border-left:4px solid {color};background:{bg};border-radius:0 8px 8px 0;">
                <div style="min-width:55px;font-size:.8rem;color:{color};font-weight:700">Leg. {row['legajo']}</div>
                <div style="flex:1">
                    <span style="font-weight:600">{row['nombre']}</span>
                    <span style="color:#666;font-size:.82rem;margin-left:8px">{row['cargo_gremial']}</span>
                </div>
                <div style="text-align:right;font-size:.8rem">
                    <div style="color:{color};font-weight:600">{row['status']}{detalle_txt}</div>
                    <div style="color:#888">Desde {row['desde']}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        buf_fdp = io.BytesIO()
        with pd.ExcelWriter(buf_fdp, engine="openpyxl") as w:
            df_fdp.to_excel(w, index=False, sheet_name="Historial FDP")
            df_fdp[df_fdp["status"]=="Activo"].to_excel(w, index=False, sheet_name="Activos")
        buf_fdp.seek(0)
        st.download_button("⬇️ Exportar a Excel", data=buf_fdp, file_name="smata_fuera_de_planta.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab_edit:
        st.markdown("### ➕ Agregar registro al padrón")
        STATUS_OPTS = ["Activo", "Desvinculado", "Reincorporado a TASA", "Cargo Político", "Fallecimiento", "Renuncia Sindicato"]
        with st.form("form_fdp_alta"):
            e1,e2,e3 = st.columns(3)
            with e1:
                n_leg  = st.text_input("Legajo *")
                n_nom  = st.text_input("Nombre y Apellido *")
            with e2:
                n_carg = st.text_input("Cargo Gremial *")
                n_desd = st.text_input("Desde (año)", value=str(date.today().year))
            with e3:
                n_stat = st.selectbox("Status", STATUS_OPTS)
                n_det  = st.text_input("Detalle / Observación")
            if st.form_submit_button("✅ Agregar", type="primary", use_container_width=True):
                if not n_leg or not n_nom or not n_carg:
                    st.error("Completá Legajo, Nombre y Cargo Gremial.")
                else:
                    nueva_f = pd.DataFrame([{"legajo":n_leg.strip(),"nombre":n_nom.strip(),
                        "cargo_gremial":n_carg,"desde":n_desd,"status":n_stat,"detalle":n_det}])
                    df_fdp = pd.concat([df_fdp, nueva_f], ignore_index=True)
                    _save_fdp(df_fdp)
                    st.success(f"✅ {n_nom} agregado."); st.rerun()

        st.markdown("---")
        st.markdown("### ✏️ Cambiar status de una persona")
        opciones_edit = [f"{r['legajo']} · {r['nombre']}" for _, r in df_fdp.iterrows()]
        sel_edit_fdp = st.selectbox("Seleccioná", opciones_edit, key="fdp_edit_sel")
        idx_edit_fdp = opciones_edit.index(sel_edit_fdp)
        row_edit = df_fdp.iloc[idx_edit_fdp]
        with st.form("form_fdp_edit"):
            c1,c2 = st.columns(2)
            with c1:
                nuevo_st  = st.selectbox("Nuevo Status", STATUS_OPTS, index=STATUS_OPTS.index(row_edit["status"]) if row_edit["status"] in STATUS_OPTS else 0)
            with c2:
                nuevo_det = st.text_input("Detalle", value=str(row_edit.get("detalle","")))
            if st.form_submit_button("💾 Guardar cambio", type="primary"):
                df_fdp.iloc[idx_edit_fdp, df_fdp.columns.get_loc("status")]  = nuevo_st
                df_fdp.iloc[idx_edit_fdp, df_fdp.columns.get_loc("detalle")] = nuevo_det
                _save_fdp(df_fdp)
                st.success("✅ Actualizado."); st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — ASIMRA
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "ASIMRA":
    st.markdown('<div class="section-title">ASIMRA — Asociación de Supervisores de la Industria Metalmecánica</div>', unsafe_allow_html=True)
    df_asimra = _load_asimra()

    # ── KPIs ──
    total_a = len(df_asimra)
    cir_a   = len(df_asimra[df_asimra["cargo_gremial"]=="CIR"])
    del_a   = len(df_asimra[df_asimra["cargo_gremial"]=="Delegado"])

    k1,k2,k3 = st.columns(3)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Representantes</div><div class="kpi-value">{total_a}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card warning"><div class="kpi-label">CIR</div><div class="kpi-value">{cir_a}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card ok"><div class="kpi-label">Delegados</div><div class="kpi-value">{del_a}</div></div>', unsafe_allow_html=True)

    tab_pad_a, tab_edit_a = st.tabs(["👥 Padrón Actual", "✏️ Editar Padrón"])

    with tab_pad_a:
        st.markdown(f"**{total_a} representantes ASIMRA activos**")
        st.markdown("")
        # CIR primero, luego Delegados
        for cargo_tipo in ["CIR", "Delegado"]:
            subset = df_asimra[df_asimra["cargo_gremial"]==cargo_tipo]
            if subset.empty: continue
            color_ct = "#E67E22" if cargo_tipo == "CIR" else "#27AE60"
            bg_ct    = "#FEF0D5" if cargo_tipo == "CIR" else "#D5F0E0"
            st.markdown(f"""<div style="background:{color_ct};color:white;padding:6px 14px;border-radius:6px;margin-bottom:8px;font-weight:700;font-size:.85rem">{cargo_tipo} — {len(subset)} personas</div>""", unsafe_allow_html=True)
            for _, row in subset.iterrows():
                posicion = str(row.get("posicion_org","")).strip()
                pos_txt  = f"<span style='color:#666;font-size:.82rem;margin-left:8px'>{posicion}</span>" if posicion else ""
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:14px;padding:10px 16px;margin-bottom:6px;border:1px solid #eee;border-radius:8px;background:#fafafa;">
                    <div style="background:{color_ct};color:white;font-weight:700;padding:8px 10px;border-radius:6px;font-size:.9rem;min-width:65px;text-align:center">Leg.<br>{row['legajo']}</div>
                    <div>
                        <div style="font-weight:700;font-size:.95rem">{row['nombre']}{pos_txt}</div>
                        <span style="background:{bg_ct};color:{color_ct};padding:2px 10px;border-radius:20px;font-size:.8rem;font-weight:600">{cargo_tipo}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown("")

        st.markdown("---")
        buf_asi = io.BytesIO()
        with pd.ExcelWriter(buf_asi, engine="openpyxl") as w:
            df_asimra.to_excel(w, index=False, sheet_name="ASIMRA")
        buf_asi.seek(0)
        st.download_button("⬇️ Exportar a Excel", data=buf_asi, file_name="asimra_padron.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab_edit_a:
        st.markdown("### ➕ Agregar representante")
        with st.form("form_asimra_alta"):
            ea1,ea2 = st.columns(2)
            with ea1:
                a_leg  = st.text_input("Legajo *")
                a_nom  = st.text_input("Nombre y Apellido *")
            with ea2:
                a_car  = st.selectbox("Cargo Gremial", ["CIR","Delegado"])
                a_pos  = st.text_input("Posición / Rol")
            if st.form_submit_button("✅ Agregar", type="primary", use_container_width=True):
                if not a_leg or not a_nom:
                    st.error("Completá Legajo y Nombre.")
                else:
                    nueva_a = pd.DataFrame([{"legajo":a_leg.strip(),"nombre":a_nom.strip(),
                        "cargo_gremial":a_car,"posicion_org":a_pos}])
                    df_asimra = pd.concat([df_asimra, nueva_a], ignore_index=True)
                    _save_asimra(df_asimra)
                    st.success(f"✅ {a_nom} agregado."); st.rerun()

        if not df_asimra.empty:
            st.markdown("---")
            st.markdown("### 🗑️ Eliminar representante")
            opciones_a = [f"{r['legajo']} · {r['nombre']}" for _, r in df_asimra.iterrows()]
            sel_del_a  = st.selectbox("Seleccioná el representante a eliminar", opciones_a, key="asimra_del_sel")
            idx_del_a  = opciones_a.index(sel_del_a)
            if st.button("🗑️ Eliminar", type="primary"):
                df_asimra = df_asimra.drop(index=idx_del_a).reset_index(drop=True)
                _save_asimra(df_asimra)
                st.success("Eliminado."); st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — HISTORIAL GREMIAL
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "Historial Gremial":
    st.markdown('<div class="section-title">Historial Gremial — Evolución del Bloque Representativo</div>', unsafe_allow_html=True)

    df_fdp    = _load_fdp()
    df_asimra = _load_asimra()
    df_pad    = load_padron()

    # ── Resumen ejecutivo cross-sindicatos ──
    smata_planta_activos = len(df_pad[df_pad["Activo"]=="Sí"])
    smata_planta_bajas   = len(df_pad[df_pad["Activo"]=="No"])
    fdp_activos  = len(df_fdp[df_fdp["status"]=="Activo"])
    fdp_hist     = len(df_fdp)
    asimra_total = len(df_asimra)

    st.markdown("""<div style="background:#1A2C5B;color:white;padding:12px 20px;border-radius:8px;margin-bottom:16px;">
        <b style="font-size:1.1rem">RESUMEN GLOBAL — Todos los sindicatos</b></div>""", unsafe_allow_html=True)

    # Mandatos
    st.markdown("**Mandatos vigentes**")
    cols_mand = st.columns(3)
    for i, (sind, m_info) in enumerate(MANDATOS.items()):
        with cols_mand[i]:
            if m_info.get("inicio"):
                st.markdown(f"""<div style="background:#EEF2FF;border-radius:8px;padding:10px 14px;margin-bottom:10px;">
                    <div style="font-weight:700;color:#2E4A9E;font-size:.9rem">{sind}</div>
                    <div style="font-size:.8rem;color:#444">Mandato {m_info['periodo']}</div>
                    <div style="font-size:.78rem;color:#666">Inicio: {m_info['inicio']} · Fin est.: {m_info['fin_estimado']}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style="background:#F8FAFC;border-radius:8px;padding:10px 14px;margin-bottom:10px;border:1px solid #eee;">
                    <div style="font-weight:700;color:#2E4A9E;font-size:.9rem">{sind}</div>
                    <div style="font-size:.8rem;color:#888">Mandato sin fecha registrada</div>
                </div>""", unsafe_allow_html=True)
    st.markdown("---")

    k1,k2,k3,k4 = st.columns(4)
    k1.markdown(f'<div class="kpi-card ok"><div class="kpi-label">SMATA Planta — Activos</div><div class="kpi-value">{smata_planta_activos}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">SMATA FDP — Activos</div><div class="kpi-value">{fdp_activos}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card warning"><div class="kpi-label">ASIMRA — Activos</div><div class="kpi-value">{asimra_total}</div></div>', unsafe_allow_html=True)
    total_rep = smata_planta_activos + fdp_activos + asimra_total
    k4.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Representantes Hoy</div><div class="kpi-value">{total_rep}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab_planta, tab_fdp, tab_resumen = st.tabs([
        "👥 SMATA Planta — Movimientos",
        "🚗 SMATA FDP — Evolución",
        "📊 Resumen Comparativo",
    ])

    # ── TAB: SMATA Planta ──
    with tab_planta:
        st.markdown("### Movimientos en el padrón SMATA Planta")
        altas  = df_pad[df_pad["Fecha Alta"].str.strip().ne("") & df_pad["Activo"].eq("Sí")]
        bajas  = df_pad[df_pad["Activo"]=="No"]

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""<div style="background:#D5F0E0;border-left:4px solid #27AE60;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:12px;">
                <div style="font-weight:700;color:#27AE60;font-size:1.1rem">✅ Altas registradas: {len(altas)}</div></div>""", unsafe_allow_html=True)
            if not altas.empty:
                for _, r in altas.sort_values("Fecha Alta", ascending=False).iterrows():
                    st.markdown(f"""<div style="padding:6px 10px;margin-bottom:4px;background:#f9f9f9;border-radius:6px;font-size:.85rem">
                        <b>{r['Nombre y Apellido']}</b> <span style="color:#888">Leg. {r['Legajo']}</span><br>
                        <span style="color:#27AE60">Alta: {r['Fecha Alta']}</span> · {r['Cargo']} · Turno {r['Turno']}</div>""", unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""<div style="background:#FCE4E4;border-left:4px solid #C0392B;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:12px;">
                <div style="font-weight:700;color:#C0392B;font-size:1.1rem">🔴 Bajas registradas: {len(bajas)}</div></div>""", unsafe_allow_html=True)
            if not bajas.empty:
                for _, r in bajas.sort_values("Fecha Baja", ascending=False).iterrows():
                    st.markdown(f"""<div style="padding:6px 10px;margin-bottom:4px;background:#f9f9f9;border-radius:6px;font-size:.85rem">
                        <b>{r['Nombre y Apellido']}</b> <span style="color:#888">Leg. {r['Legajo']}</span><br>
                        <span style="color:#C0392B">Baja: {r['Fecha Baja']}</span> · {r.get('Motivo Baja','')}</div>""", unsafe_allow_html=True)

    # ── TAB: SMATA FDP ──
    with tab_fdp:
        st.markdown("### Evolución SMATA Fuera de Planta (2008 — hoy)")

        STATUS_COLORS_FDP = {
            "Activo":               ("#27AE60","#D5F0E0"),
            "Desvinculado":         ("#C0392B","#FCE4E4"),
            "Reincorporado a TASA": ("#E67E22","#FEF0D5"),
            "Cargo Político":       ("#8E44AD","#F3E8FF"),
            "Fallecimiento":        ("#4A4A4A","#EBEBEB"),
            "Renuncia Sindicato":   ("#7F8C8D","#ECF0F1"),
        }

        for status_tipo in ["Activo","Reincorporado a TASA","Cargo Político","Desvinculado"]:
            subset = df_fdp[df_fdp["status"]==status_tipo].sort_values("desde")
            if subset.empty: continue
            color, bg = STATUS_COLORS_FDP[status_tipo]
            icono = {"Activo":"✅","Reincorporado a TASA":"🔄","Cargo Político":"🏛️","Desvinculado":"🔴"}.get(status_tipo,"•")
            st.markdown(f"""<div style="background:{color};color:white;padding:8px 16px;border-radius:6px;margin:12px 0 8px 0;font-weight:700">
                {icono} {status_tipo} — {len(subset)} personas</div>""", unsafe_allow_html=True)
            for _, row in subset.iterrows():
                detalle_txt = f" · {row['detalle']}" if str(row.get("detalle","")).strip() else ""
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 14px;margin-bottom:4px;background:{bg};border-radius:6px;">
                    <div><b>{row['nombre']}</b> <span style="color:#666;font-size:.82rem">Leg. {row['legajo']}</span></div>
                    <div style="text-align:right;font-size:.82rem;color:#444">{row['cargo_gremial']}{detalle_txt}<br><span style="color:{color}">Desde {row['desde']}</span></div>
                </div>""", unsafe_allow_html=True)

        # Línea de tiempo por año de ingreso
        st.markdown("---")
        st.markdown("### 📅 Ingresos por año")
        desde_num = pd.to_numeric(df_fdp["desde"].str.extract(r"(\d{4})")[0], errors="coerce")
        por_anio  = desde_num.value_counts().sort_index()
        if not por_anio.empty:
            st.bar_chart(por_anio.rename("Ingresos"), color="#2E4A9E")

    # ── TAB: Resumen comparativo ──
    with tab_resumen:
        st.markdown("### Composición actual del bloque gremial")

        # Tabla resumen
        resumen_data = [
            {"Sindicato":"SMATA Planta","Activos":smata_planta_activos,"Bajas/Histórico":smata_planta_bajas,"Total Histórico":smata_planta_activos+smata_planta_bajas},
            {"Sindicato":"SMATA Fuera de Planta","Activos":fdp_activos,"Bajas/Histórico":fdp_hist-fdp_activos,"Total Histórico":fdp_hist},
            {"Sindicato":"ASIMRA","Activos":asimra_total,"Bajas/Histórico":0,"Total Histórico":asimra_total},
        ]
        df_resumen = pd.DataFrame(resumen_data)
        st.dataframe(df_resumen, use_container_width=True, hide_index=True)

        st.markdown("")
        st.markdown("### SMATA Fuera de Planta — breakdown por status")
        fdp_status = df_fdp["status"].value_counts()
        for st_name, st_count in fdp_status.items():
            color, bg = STATUS_COLORS_FDP.get(st_name, ("#2E4A9E","#EEF2FF"))
            pct = round(st_count / len(df_fdp) * 100, 1)
            st.markdown(f"""<div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-size:.85rem;font-weight:600">{st_name}</span>
                    <span style="font-size:.85rem;font-weight:700;color:{color}">{st_count} personas ({pct}%)</span>
                </div>
                <div style="background:#eee;border-radius:4px;height:10px;">
                    <div style="background:{color};width:{pct}%;height:10px;border-radius:4px"></div>
                </div></div>""", unsafe_allow_html=True)

        st.markdown("")
        st.markdown("### ASIMRA — distribución por cargo")
        for cargo_n, cargo_c in df_asimra["cargo_gremial"].value_counts().items():
            pct_a = round(cargo_c / len(df_asimra) * 100, 1)
            color_a = "#E67E22" if cargo_n == "CIR" else "#27AE60"
            st.markdown(f"""<div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-size:.85rem;font-weight:600">{cargo_n}</span>
                    <span style="font-size:.85rem;font-weight:700;color:{color_a}">{cargo_c} personas ({pct_a}%)</span>
                </div>
                <div style="background:#eee;border-radius:4px;height:10px;">
                    <div style="background:{color_a};width:{pct_a}%;height:10px;border-radius:4px"></div>
                </div></div>""", unsafe_allow_html=True)

        st.markdown("---")
        buf_hist = io.BytesIO()
        with pd.ExcelWriter(buf_hist, engine="openpyxl") as w:
            df_resumen.to_excel(w, index=False, sheet_name="Resumen Global")
            df_fdp.to_excel(w, index=False, sheet_name="SMATA FDP")
            df_asimra.to_excel(w, index=False, sheet_name="ASIMRA")
            df_pad.to_excel(w, index=False, sheet_name="SMATA Planta Padrón")
        buf_hist.seek(0)
        st.download_button("⬇️ Exportar Historial Completo", data=buf_hist,
            file_name="historial_gremial_completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA — GENERAR REPORTE PPT
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "Generar Reporte PPT":
    st.markdown('<div class="section-title">Generar Reporte de Movilidad Gremial en PowerPoint</div>', unsafe_allow_html=True)
    st.markdown("Genera el reporte completo en PPT — 12 slides con analisis automatico de los datos del registro.")

    df_all = load_data(_mtime=_get_mtime(DATA_FILE))

    if df_all.empty:
        st.warning("No hay registros cargados. Importa el historico primero.")
    else:
        df_all["_fecha"] = _parsear_fechas(df_all)
        fechas_validas = df_all["_fecha"].dropna()

        if fechas_validas.empty:
            st.error("No se pudieron interpretar las fechas del registro.")
        else:
            fecha_min_data = fechas_validas.min().date()
            fecha_max_data = fechas_validas.max().date()
            st.markdown(f"**Base cargada:** {len(df_all)} registros  ·  Rango: {fecha_min_data.strftime('%d/%m/%Y')} — {fecha_max_data.strftime('%d/%m/%Y')}")
            st.markdown("---")

            fc1, fc2 = st.columns(2)
            with fc1:
                ppt_desde = st.date_input("Periodo desde", value=fecha_min_data, format="DD/MM/YYYY", key="ppt_desde")
            with fc2:
                ppt_hasta = st.date_input("Periodo hasta", value=fecha_max_data, format="DD/MM/YYYY", key="ppt_hasta")

            df_prev = df_all[
                (df_all["_fecha"] >= pd.Timestamp(ppt_desde)) &
                (df_all["_fecha"] <= pd.Timestamp(ppt_hasta))
            ].copy()
            df_prev["_es_desvio"] = df_prev["Movilidad Gremial x Semana x Dia"].apply(es_desvio)

            if not df_prev.empty:
                n_dev_prev = int(df_prev["_es_desvio"].sum())
                tasa_prev  = round(n_dev_prev / len(df_prev) * 100, 1) if len(df_prev) > 0 else 0
                p1,p2,p3 = st.columns(3)
                p1.markdown(f'<div class="kpi-card"><div class="kpi-label">Registros en el periodo</div><div class="kpi-value">{len(df_prev)}</div></div>', unsafe_allow_html=True)
                p2.markdown(f'<div class="kpi-card danger"><div class="kpi-label">Desvios</div><div class="kpi-value">{n_dev_prev}</div></div>', unsafe_allow_html=True)
                p3.markdown(f'<div class="kpi-card {"danger" if tasa_prev>15 else "warning" if tasa_prev>10 else "ok"}"><div class="kpi-label">Tasa</div><div class="kpi-value">{tasa_prev}%</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            if st.button("Generar PPT", type="primary", use_container_width=True, disabled=df_prev.empty):
                with st.spinner("Generando reporte..."):
                    try:
                        from generar_reporte_pptx import generar_reporte_bytes
                        df_export = df_prev.drop(columns=["_fecha","_es_desvio"], errors="ignore")
                        periodo_lbl = f"{ppt_desde.strftime('%d/%m/%Y')} — {ppt_hasta.strftime('%d/%m/%Y')}"
                        n_del = df_export["Legajo"].nunique() if "Legajo" in df_export.columns else "?"
                        ppt_bytes = generar_reporte_bytes(df_export, periodo_lbl, n_del)
                        fname = f"Movilidad_Gremial_{ppt_desde.strftime('%d%m%Y')}_{ppt_hasta.strftime('%d%m%Y')}.pptx"
                        st.success(f"Reporte generado — {len(ppt_bytes)//1024} KB")
                        st.download_button(
                            label="Descargar PPT",
                            data=ppt_bytes,
                            file_name=fname,
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True, type="primary"
                        )
                    except ImportError:
                        st.error("No se encontro generar_reporte_pptx.py. Asegurate de que este en la misma carpeta que app.py.")
                    except Exception as e:
                        st.error(f"Error al generar el PPT: {e}")