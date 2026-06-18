"""
importar_analisis.py
Convierte el Excel de Analisis.xlsx (solapa Datos, formato semanal)
al formato estándar de registro_gremial.csv que usa la app.

Cada fila del Excel = 1 delegado x 1 semana, con hasta 5 días (Fecha 1-5).
Cada celda = valor del día (Cumple, VACACIONES, o tipo de desvío).
Las celdas vacías/NaN = Cumple implícito.

El resultado: 1 fila por delegado por día = mismo formato que registro_gremial.
"""

import pandas as pd
import io

# ── Semanas reales por mes ─────────────────────────────────────────────────────
# Cada entrada es la fecha de inicio de la semana de control
SEMANAS_MES = {
    'Noviembre': ['17/11/2025', '24/11/2025'],
    'Diciembre': ['01/12/2025', '08/12/2025', '15/12/2025', '22/12/2025', '29/12/2025'],
    'Enero':     ['05/01/2026', '26/01/2026'],
    'Febrero':   ['09/02/2026', '16/02/2026', '23/02/2026'],
    'Marzo':     ['02/03/2026', '09/03/2026'],
}

# ── Mapeo de valores del Excel → Movilidad estándar ───────────────────────────
DESVIOS_MAP = {
    '17 movilidad gremial elecciones': 'No Cumple',
    'movilidad gremial':               'No Cumple',
    'actividad gremial':               'No Cumple',
    'act gremial (8m)':                'Excede 5/10 min',
    'act gremial (u)':                 'No Cumple',
    'cir':                             'No Cumple',
    'cir -30min':                      'Excede 5/10 min',
    'mg 2.5':                          'Excede + 10/20min',
    'mant especial':                   'No Cumple',
    'tareas gremiales + 5':            'Supera + 1/2hs',
    'tareas limitadas':                'No Cumple',
    'reingreso +2':                    'Excede 5/10 min',
    'compezó tn':                      'Cambia de turno',
    'compenzó tt':                     'Cambia de turno',
    'excede mg + 3':                   'Excede + 10/20min',
    'excede mg + 3hs':                 'Excede + 10/20min',
    'excede mg + 4':                   'Excede + 10/20min',
    'excede mg + 5':                   'Supera + 1/2hs',
    'excede mg +3':                    'Excede + 10/20min',
    'excede mg +4':                    'Excede + 10/20min',
    'excede mg +5/20´':                'Supara + 1/2hs',
    'excede de 5 a 20 min':            'Excede + 10/20min',
    'extención de mg':                 'Excede + 10/20min',
    'excede mg + 3\npdp 2´':           'Excede + 10/20min',
    'excede mg + 3\nreunión sin aviso (plan stop)': 'Excede + 10/20min',
    'llt charla 5':                    'Excede 5/10 min',
    'llt charla 5´':                   'Excede 5/10 min',
    'llt charla 5´\nexcede mg +5hs':   'Excede 5/10 min',
    'llt charla 5´\nexcede mg +5hs\n': 'Excede 5/10 min',
    'llt\nexcede mg +3':               'Excede + 10/20min',
    'llt mov':                         'Excede 5/10 min',
    'llt':                             'Excede 5/10 min',
    'a charla 5´':                     'Excede 5/10 min',
    'a charla 5´\nexcede mg + 3':      'Excede + 10/20min',
    'a charla 5´\nst':                 'Excede 5/10 min',
    'a charla 5':                      'Excede 5/10 min',
    'st':                              'No Cumple',
    'st art':                          'No Cumple',
    'retiro sin cobertura':            'No Cumple',
    'se retiran 10hs por movilización':'Supera + 1/2hs',
    'se retiran 11hs por movilización':'Supera + 1/2hs',
    'no asistieron \n(movilizacion)':  'Supera semanal',
    'reunión sin aviso (plan stop)':   'No Cumple',
    'paro/movilización.':              'No Cumple',
    'ausente':                         'No Cumple',
    'baja medica':                     'No Cumple',
    'baja médica':                     'No Cumple',
    'lic médica':                      'No Cumple',
    'lic. varias ':                    'No Cumple',
    'lic. varias':                     'No Cumple',
    'licencia art':                    'No Cumple',
    'licencia médica':                 'No Cumple',
    'art':                             'No Cumple',
    'enf inculpable':                  'No Cumple',
    'familiar enfermo':                'No Cumple',
    'fecha 5':                         'No Cumple',
    'cumple parcial \nsale 20:40 hasta fin de turno': 'No Cumple',
    'cumple parcial  \nsale 07:40 y el segundo  bloque': 'No Cumple',
    'no cumple':                       'No Cumple',
}

MOTIVO_MAP = {
    'movilidad gremial':               'REUNION CIR',
    '17 movilidad gremial elecciones': 'ASAMBLEA',
    'actividad gremial':               'ASAMBLEA',
    'paro/movilización.':              'ASAMBLEA',
    'no asistieron \n(movilizacion)':  'ASAMBLEA',
    'se retiran 10hs por movilización':'ASAMBLEA',
    'se retiran 11hs por movilización':'ASAMBLEA',
    'cir':                             'REUNION CIR',
    'baja medica':                     'AUSENTISMO LINEA',
    'baja médica':                     'AUSENTISMO LINEA',
    'lic médica':                      'AUSENTISMO LINEA',
    'licencia médica':                 'AUSENTISMO LINEA',
    'licencia art':                    'AUSENTISMO LINEA',
    'art':                             'AUSENTISMO LINEA',
    'st art':                          'AUSENTISMO LINEA',
    'enf inculpable':                  'AUSENTISMO LINEA',
}

LLT_MAP = {
    'llt charla 5':    'LLT CON AVISO',
    'llt charla 5´':   'LLT CON AVISO',
    'llt':             'LLT SIN AVISO',
    'llt mov':         'LLT CON AVISO',
    'a charla 5´':     'LLT CON AVISO',
    'a charla 5':      'LLT CON AVISO',
    'a charla 5´\nst': 'LLT CON AVISO',
}

DELEGADOS_INFO = {
    "7232":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"CIR",     "reporta":"Mauro Bringas"},
    "12738":  {"cuerpo":"ENSAMBLE & MOTORES","cargo":"CIR",     "reporta":"Juan Bizzotto"},
    "605097": {"cuerpo":"MH",                "cargo":"CIR",     "reporta":"Martin Gentilini"},
    "8266":   {"cuerpo":"MH",                "cargo":"CIR",     "reporta":"Carlos Fuentes"},
    "10018":  {"cuerpo":"QC",                "cargo":"CIR",     "reporta":"Marcelo Martinez"},
    "7047":   {"cuerpo":"EXTERNOS",          "cargo":"CIR",     "reporta":"Hugo Taborda"},
    "7652":   {"cuerpo":"SOLDADURA",         "cargo":"CIR",     "reporta":"Faustino Carrasco"},
    "12538":  {"cuerpo":"SOLDADURA",         "cargo":"CIR",     "reporta":"Leonardo Gonzalez"},
    "9500":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Jose Gorosito"},
    "13264":  {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Andres Galdames"},
    "1772":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Cristian Moreno"},
    "6306":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Fernando Canerhoff"},
    "7888":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Fernando Canerhoff"},
    "8248":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Jose Ibanez"},
    "5228":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Walter Herrero"},
    "3675":   {"cuerpo":"MANTENIMIENTO",     "cargo":"Delegado","reporta":"Ariel Amarillo"},
    "1446":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Esteban Kroger"},
    "12398":  {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Facundo Bustos"},
    "12422":  {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Facundo Bustos"},
    "6807":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Juan Bizzotto"},
    "1802":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Marcos Furtado"},
    "12338":  {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Marcos Furtado"},
    "4553":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Marcos Furtado"},
    "9667":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Maximiliano Ellemberger"},
    "604590": {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Pablo Lopez"},
    "7001":   {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Pablo Lopez"},
    "9565":   {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Edmundo Lugo"},
    "6713":   {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Ignacio Ibar"},
    "4729":   {"cuerpo":"MH",                "cargo":"Delegado","reporta":"Jose Mateo"},
    "6783":   {"cuerpo":"MH",                "cargo":"Delegado","reporta":"Martin Gentilini"},
    "6287":   {"cuerpo":"MH",                "cargo":"Delegado","reporta":"Emanuel Pacher"},
    "13400":  {"cuerpo":"MH",                "cargo":"Delegado","reporta":"Ramiro Elizaga"},
    "4583":   {"cuerpo":"MH",                "cargo":"Delegado","reporta":"Jose Mateo"},
    "8193":   {"cuerpo":"ENSAMBLE & MOTORES","cargo":"Delegado","reporta":"Cesar Cuenca"},
    "1983":   {"cuerpo":"MH",                "cargo":"Delegado","reporta":"Carlos Fuentes"},
    "837":    {"cuerpo":"PINTURA",           "cargo":"Delegado","reporta":"Matias Cardenas"},
    "6717":   {"cuerpo":"PINTURA",           "cargo":"Delegado","reporta":"Ariel Rupp"},
    "6825":   {"cuerpo":"PINTURA",           "cargo":"Delegado","reporta":"Javier Werner"},
    "11878":  {"cuerpo":"PINTURA",           "cargo":"Delegado","reporta":"Javier Werner"},
    "8273":   {"cuerpo":"PINTURA",           "cargo":"Delegado","reporta":"Cesar Bentancur"},
    "1748":   {"cuerpo":"PINTURA",           "cargo":"Delegado","reporta":"Javier Werner"},
    "573":    {"cuerpo":"MANTENIMIENTO",     "cargo":"Delegado","reporta":"Nicolas Echeverria"},
    "4394":   {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Julian Lopez"},
    "4310":   {"cuerpo":"QC",                "cargo":"Delegado","reporta":"Marcelo Martinez"},
    "5740":   {"cuerpo":"QC",                "cargo":"Delegado","reporta":"Ariel Sena"},
    "4934":   {"cuerpo":"QC",                "cargo":"Delegado","reporta":"Ariel Sena"},
    "8641":   {"cuerpo":"QC",                "cargo":"Delegado","reporta":"Ruben Ragusa"},
    "1645":   {"cuerpo":"EXTERNOS",          "cargo":"Delegado","reporta":"Diego Vargas"},
    "12376":  {"cuerpo":"EXTERNOS",          "cargo":"Delegado","reporta":"Diego Irasuegui"},
    "1858":   {"cuerpo":"EXTERNOS",          "cargo":"Delegado","reporta":"Matias Medina"},
    "12643":  {"cuerpo":"EXTERNOS",          "cargo":"Delegado","reporta":"Carlos Demierre"},
    "7264":   {"cuerpo":"EXTERNOS",          "cargo":"Delegado","reporta":"Jose Martinez"},
    "7942":   {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Diego Mendieta"},
    "605098": {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Leonardo Gonzalez"},
    "6650":   {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Juan Lindner"},
    "7092":   {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Federico Medina"},
    "9412":   {"cuerpo":"SOLDADURA",         "cargo":"Delegado","reporta":"Faustino Carrasco"},
    "8235":   {"cuerpo":"MANTENIMIENTO",     "cargo":"Delegado","reporta":"Victor Garcia Calderon"},
}

COLUMNS_OUT = [
    "Legajo","Nombre y Apellido","Cuerpo Gremial","Sector","Cargo",
    "Turno","Reporta a","Fecha",
    "Movilidad Gremial x Semana x Dia","Motivo Excedencia",
    "Licencia","Informacion Licencia",
    "LLT/Ausencia Inj","Observaciones Extras",
    "Motivo (Detallar desvios)","Accion"
]


def convertir_analisis_a_registro(archivo):
    """
    Recibe un archivo Excel (path o file-like) con solapa 'Datos'.
    Devuelve un DataFrame en formato registro_gremial.csv.
    """
    # Leer solapa Datos
    df_raw = pd.read_excel(archivo, sheet_name='Datos', header=0, dtype=str)
    # La fila 0 es el header real
    df_raw.columns = df_raw.iloc[0].tolist()
    df_raw = df_raw.iloc[1:].reset_index(drop=True)

    rows_out = []
    sem_counter = {}

    for _, row in df_raw.iterrows():
        mes = str(row.get('Mes', '')).strip()
        leg = str(row.get('Legajo', '')).strip()
        nom = str(row.get('Nombre', '')).strip()
        sec = str(row.get('Sector', '')).strip()
        tur = str(row.get('Turno', '')).strip()

        if not mes or mes == 'nan' or mes not in SEMANAS_MES:
            continue
        if not leg or leg == 'nan':
            continue

        semanas = SEMANAS_MES[mes]
        key = (leg, mes)
        idx = sem_counter.get(key, 0)
        sem_counter[key] = idx + 1
        if idx >= len(semanas):
            continue

        fecha_sem = semanas[idx]
        del_info  = DELEGADOS_INFO.get(leg, {})
        cuerpo    = del_info.get('cuerpo', '')
        cargo     = del_info.get('cargo', 'Delegado')
        reporta   = del_info.get('reporta', '')

        for fecha_col in ['Fecha 1', 'Fecha 2', 'Fecha 3', 'Fecha 4', 'Fecha 5']:
            val_raw = str(row.get(fecha_col, '')).strip()
            val_low = val_raw.lower().strip()
            is_nan  = val_raw in ('', 'nan', 'None', 'NaN')

            if is_nan or 'cumple' in val_low or 'vacac' in val_low:
                movilidad = "Cumple"
                motivo    = "NO APLICA"
                licencia  = "VACACIONES" if 'vacac' in val_low else ""
                llt       = ""
                obs       = ""
                info_lic  = ""
            else:
                movilidad = DESVIOS_MAP.get(val_low, "No Cumple")
                motivo    = MOTIVO_MAP.get(val_low, "SIN INFORMACION")
                llt       = LLT_MAP.get(val_low, "")
                licencia  = ""
                obs       = val_raw
                info_lic  = val_raw

            rows_out.append({
                "Legajo":                           leg,
                "Nombre y Apellido":                nom,
                "Cuerpo Gremial":                   cuerpo,
                "Sector":                           sec,
                "Cargo":                            cargo,
                "Turno":                            tur,
                "Reporta a":                        reporta,
                "Fecha":                            fecha_sem,
                "Movilidad Gremial x Semana x Dia": movilidad,
                "Motivo Excedencia":                motivo,
                "Licencia":                         licencia,
                "Informacion Licencia":             info_lic,
                "LLT/Ausencia Inj":                llt,
                "Observaciones Extras":             obs,
                "Motivo (Detallar desvios)":        val_raw if movilidad != "Cumple" else "",
                "Accion":                           ""
            })

    return pd.DataFrame(rows_out, columns=COLUMNS_OUT)
