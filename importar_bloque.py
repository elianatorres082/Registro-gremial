"""
importar_bloque.py
Convierte el Excel Bloque_Gremial.xlsx (una solapa por semana) al formato
estándar de registro_gremial.csv.

Por defecto solo importa solapas desde Abril en adelante.
Se puede pasar meses_incluir para controlar qué meses importar.
"""

import pandas as pd
import re

MESES_MAP = {
    'ENERO':'01','FEBRERO':'02','MARZO':'03','ABRIL':'04',
    'MAYO':'05','JUNIO':'06','JULIO':'07','AGOSTO':'08',
    'SEPTIEMBRE':'09','OCTUBRE':'10','NOVIEMBRE':'11','DICIEMBRE':'12'
}

MESES_DESDE_ABRIL = ['ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE']

COL_MAP = {
    'legajo':                           'Legajo',
    'nombre y apellido':                'Nombre y Apellido',
    'cuerpo gremial':                   'Cuerpo Gremial',
    'sector':                           'Sector',
    'cargo':                            'Cargo',
    'turno':                            'Turno',
    'reporta a':                        'Reporta a',
    'movilidad gremial x semana x dia': 'Movilidad Gremial x Semana x Dia',
    'motivo excedencia':                'Motivo Excedencia',
    'fecha':                            'Fecha',
    'licencia':                         'Licencia',
    'motivo licencia':                  'Informacion Licencia',
    'informacion licencia':             'Informacion Licencia',
    'observaciones extras':             'Observaciones Extras',
    'llt/ausencia inj':                 'LLT/Ausencia Inj',
    'acción':                           'Accion',
    'accion':                           'Accion',
}

COLUMNS_OUT = [
    "Legajo","Nombre y Apellido","Cuerpo Gremial","Sector","Cargo",
    "Turno","Reporta a","Fecha","Movilidad Gremial x Semana x Dia",
    "Motivo Excedencia","Licencia","Informacion Licencia",
    "LLT/Ausencia Inj","Observaciones Extras","Motivo (Detallar desvios)","Accion"
]


def _fecha_de_solapa(nombre):
    """Extrae la fecha de inicio de semana del nombre de la solapa."""
    # Patrón DD.MM explícito (ej: 06.04, 13.04)
    m = re.search(r'(\d{2})[\.\/](\d{2})', nombre)
    if m:
        dia, mes_n = m.group(1), m.group(2)
        mes_int = int(mes_n)
        anio = "2025" if mes_int >= 10 else "2026"
        return f"{dia}/{mes_n}/{anio}"
    # Patrón "Semana N AL M" con mes en el nombre
    for mes_nombre, mes_num in MESES_MAP.items():
        if mes_nombre in nombre.upper():
            dm = re.search(r'[Ss]emana\s+\.?(\d{1,2})', nombre)
            if dm:
                dia = dm.group(1).zfill(2)
                anio = "2025" if int(mes_num) >= 10 else "2026"
                return f"{dia}/{mes_num}/{anio}"
    return ""


def _solapa_es_de_meses(nombre, meses):
    """Devuelve True si la solapa pertenece a alguno de los meses indicados."""
    nombre_upper = nombre.upper()
    return any(mes.upper() in nombre_upper for mes in meses)


def convertir_bloque_a_registro(archivo, meses_incluir=None):
    """
    Recibe archivo Excel (path o file-like) Bloque_Gremial.xlsx.
    meses_incluir: lista de meses a incluir, ej ['ABRIL','MAYO','JUNIO'].
                   Por defecto incluye todo desde Abril.
    Devuelve DataFrame en formato registro_gremial.csv.
    """
    if meses_incluir is None:
        meses_incluir = MESES_DESDE_ABRIL

    xl = pd.ExcelFile(archivo)
    solapas = [s for s in xl.sheet_names if _solapa_es_de_meses(s, meses_incluir)]

    rows_out = []
    solapas_procesadas = []

    for solapa in solapas:
        fecha_sem = _fecha_de_solapa(solapa)

        try:
            df_raw = xl.parse(solapa, header=None, dtype=str)
        except Exception:
            continue

        # Encontrar fila de header (la que tiene 'Legajo')
        header_row = None
        for i in range(min(5, len(df_raw))):
            row_vals = [str(v).lower().strip() for v in df_raw.iloc[i].values
                        if pd.notna(v) and str(v).strip() not in ('nan', '')]
            if 'legajo' in row_vals:
                header_row = i
                break
        if header_row is None:
            continue

        df = xl.parse(solapa, header=header_row, dtype=str)
        df = df.dropna(how='all').reset_index(drop=True)

        # Normalizar nombres de columna
        rename = {}
        for col in df.columns:
            cl = str(col).lower().strip()
            if cl in COL_MAP:
                rename[col] = COL_MAP[cl]
        df = df.rename(columns=rename)

        # Eliminar filas de header repetido
        if 'Legajo' in df.columns:
            df = df[
                df['Legajo'].notna() &
                (df['Legajo'].str.strip() != '') &
                (df['Legajo'].str.lower().str.strip() != 'legajo')
            ]

        solapas_procesadas.append(solapa)

        for _, row in df.iterrows():
            leg = str(row.get('Legajo', '')).strip()
            if not leg or leg == 'nan':
                continue

            movilidad = str(row.get('Movilidad Gremial x Semana x Dia', '')).strip()
            if movilidad in ('nan', 'None', ''):
                movilidad = 'Cumple'

            # Fecha: usar la columna Fecha si tiene fecha real, si no usar fecha de solapa
            fecha_col = str(row.get('Fecha', '')).strip()
            if fecha_col and fecha_col not in ('nan', 'NaT', 'None', ''):
                m_ts = re.search(r'(\d{4})-(\d{2})-(\d{2})', fecha_col)
                if m_ts:
                    fecha_final = f"{m_ts.group(3)}/{m_ts.group(2)}/{m_ts.group(1)}"
                else:
                    m_d = re.search(r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})', fecha_col)
                    if m_d:
                        a, b, c = m_d.group(1), m_d.group(2), m_d.group(3)
                        yr = int(c) if len(c) == 4 else 2000 + int(c)
                        if int(a) > 31:
                            fecha_final = f"{b.zfill(2)}/{a.zfill(2)}/{yr}"
                        else:
                            fecha_final = f"{a.zfill(2)}/{b.zfill(2)}/{yr}"
                    else:
                        fecha_final = fecha_sem
            else:
                fecha_final = fecha_sem

            def clean(val):
                v = str(row.get(val, '')).strip()
                return '' if v in ('nan', 'None', 'NaN') else v

            rows_out.append({
                "Legajo":                           leg,
                "Nombre y Apellido":                clean('Nombre y Apellido'),
                "Cuerpo Gremial":                   clean('Cuerpo Gremial'),
                "Sector":                           clean('Sector'),
                "Cargo":                            clean('Cargo'),
                "Turno":                            clean('Turno'),
                "Reporta a":                        clean('Reporta a'),
                "Fecha":                            fecha_final,
                "Movilidad Gremial x Semana x Dia": movilidad,
                "Motivo Excedencia":                clean('Motivo Excedencia'),
                "Licencia":                         clean('Licencia'),
                "Informacion Licencia":             clean('Informacion Licencia'),
                "LLT/Ausencia Inj":                clean('LLT/Ausencia Inj'),
                "Observaciones Extras":             clean('Observaciones Extras'),
                "Motivo (Detallar desvios)":        clean('Observaciones Extras'),
                "Accion":                           clean('Accion'),
            })

    df_out = pd.DataFrame(rows_out, columns=COLUMNS_OUT)
    return df_out, solapas_procesadas
