/**
 * Generador automático de reporte PPT — Movilidad Gremial Toyota Argentina
 * Lee el registro_gremial.csv y genera un PPT con el mismo análisis que el reporte manual.
 *
 * Uso:  node generar_reporte.js <path_csv> [fecha_desde] [fecha_hasta]
 *   ej: node generar_reporte.js /path/registro_gremial.csv 01/11/2025 31/03/2026
 */

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

// ─── Paleta de colores ────────────────────────────────────────────────────────
const C = {
  navy:      "1A2C5B",
  blue:      "2E4A9E",
  blueLight: "EEF2FF",
  red:       "C0392B",
  redLight:  "FCE4E4",
  orange:    "E67E22",
  orangeLight:"FEF3C7",
  green:     "27AE60",
  greenLight:"D5F0E0",
  purple:    "8E44AD",
  gray:      "64748B",
  grayLight: "F8FAFC",
  grayBorder:"E2E8F0",
  white:     "FFFFFF",
  black:     "1E293B",
};

// ─── Helpers ─────────────────────────────────────────────────────────────────
function pct(n, total) { return total > 0 ? Math.round(n / total * 1000) / 10 : 0; }
function fmt_pct(v) { return v.toFixed(1) + "%"; }
function addSlideHeader(pres, slide, title, subtitle = "") {
  slide.background = { color: C.white };
  // título con fondo navy
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.85, fill: { color: C.navy }, line: { color: C.navy }
  });
  slide.addText(title.toUpperCase(), {
    x: 0.35, y: 0, w: 9.3, h: 0.85, fontSize: 17, bold: true, color: C.white,
    fontFace: "Calibri", valign: "middle", margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.35, y: 0.85, w: 9.3, h: 0.32, fontSize: 10, color: C.gray,
      fontFace: "Calibri", valign: "middle", margin: 0
    });
  }
}
function makeShadow() {
  return { type: "outer", color: "000000", blur: 6, offset: 2, angle: 45, opacity: 0.10 };
}
function kpiCard(pres, slide, x, y, w, h, label, value, sub, borderColor) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, fill: { color: C.white }, line: { color: C.grayBorder, width: 1 },
    shadow: makeShadow(), rectRadius: 0.08
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h: 0.055, fill: { color: borderColor }, line: { color: borderColor }
  });
  slide.addText(label.toUpperCase(), {
    x: x + 0.15, y: y + 0.12, w: w - 0.3, h: 0.22,
    fontSize: 7.5, color: C.gray, fontFace: "Calibri", bold: false, charSpacing: 1
  });
  slide.addText(String(value), {
    x: x + 0.15, y: y + 0.32, w: w - 0.3, h: 0.52,
    fontSize: 36, bold: true, color: C.black, fontFace: "Calibri", valign: "middle"
  });
  if (sub) {
    slide.addText(sub, {
      x: x + 0.15, y: y + 0.82, w: w - 0.3, h: 0.22,
      fontSize: 8, color: C.gray, fontFace: "Calibri"
    });
  }
}

// ─── Leer y parsear CSV ───────────────────────────────────────────────────────
function parseCSV(csvPath) {
  const lines = fs.readFileSync(csvPath, "utf8").split("\n").filter(l => l.trim());
  if (lines.length < 2) return [];
  const headers = lines[0].split(",").map(h => h.trim().replace(/^"|"$/g, ""));
  return lines.slice(1).map(line => {
    // Simple CSV parse (handles quoted fields)
    const cols = [];
    let cur = "", inQ = false;
    for (let i = 0; i < line.length; i++) {
      if (line[i] === '"') { inQ = !inQ; continue; }
      if (line[i] === ',' && !inQ) { cols.push(cur.trim()); cur = ""; continue; }
      cur += line[i];
    }
    cols.push(cur.trim());
    const obj = {};
    headers.forEach((h, i) => { obj[h] = (cols[i] || "").trim(); });
    return obj;
  }).filter(r => r["Nombre y Apellido"] && r["Nombre y Apellido"] !== "Nombre y Apellido");
}

function parseDate(s) {
  if (!s) return null;
  const parts = s.split(/[\/\-]/);
  if (parts.length === 3) {
    const [a, b, c] = parts.map(Number);
    if (a > 31) return new Date(a, b - 1, c);   // YYYY-MM-DD
    if (c > 31) return new Date(c, b - 1, a);   // DD/MM/YYYY
    return new Date(c + 2000, b - 1, a);         // DD/MM/YY
  }
  return null;
}

function filterByDate(rows, desde, hasta) {
  if (!desde && !hasta) return rows;
  return rows.filter(r => {
    const d = parseDate(r["Fecha"]);
    if (!d) return false;
    if (desde && d < desde) return false;
    if (hasta && d > hasta) return false;
    return true;
  });
}

// ─── Clasificar motivo de desvío ──────────────────────────────────────────────
const DESVIOS_LOWER = [
  "no cumple", "excede -5min", "excede 5/10 min",
  "excede + 10/20min", "supera + 1/2hs", "supera semana completa",
  "genera pdl", "cambia de turno"
].map(s => s.trim().toLowerCase());

function isDesvio(row) {
  return DESVIOS_LOWER.includes((row["Movilidad Gremial x Semana x Dia"] || "").trim().toLowerCase());
}

function clasificarMotivo(row) {
  const mov = (row["Movilidad Gremial x Semana x Dia"] || "").trim().toLowerCase();
  const motExc = (row["Motivo Excedencia"] || "").trim().toLowerCase();
  const lic = (row["Licencia"] || "").trim().toLowerCase();
  const llt = (row["LLT/Ausencia Inj"] || "").trim().toLowerCase();
  const obs = (row["Observaciones Extras"] || "").trim().toLowerCase();
  const motDesv = (row["Motivo (Detallar desvios)"] || "").trim().toLowerCase();
  const todo = [mov, motExc, lic, llt, obs, motDesv].join(" ");

  if (todo.includes("llt") || todo.includes("charla") || todo.includes("charla 5")) return "LLT / Charla";
  if (todo.includes("art") || todo.includes("médica") || todo.includes("medica") || todo.includes("enfermedad") || todo.includes("licencia")) return "Ausencia / Licencia Médica o ART";
  if (todo.includes("no cumple") || todo.includes("incumplimiento") || todo.includes("injustificada") || todo.includes("inj")) return "Incumplimiento / Ausencia sin justificar";
  if (mov.includes("excede") || mov.includes("supera") || todo.includes("exceso") || todo.includes("excede")) return "Exceso en Movilidad Gremial (tiempo)";
  if (motExc.includes("asamblea") || motExc.includes("moviliz") || todo.includes("movilizaci")) return "Movilización / Actividad Gremial";
  if (motExc.includes("reunion") || motExc.includes("reunión") || motExc.includes("gremial")) return "Movilización / Actividad Gremial";
  if (mov.includes("cambia de turno") || mov.includes("genera pdl")) return "Actividad Gremial (otras)";
  if (todo.includes("gremial") || todo.includes("sindicato") || todo.includes("delegado")) return "Movilización / Actividad Gremial";
  return "Otros";
}

const MESES_ES = {
  0:"Enero", 1:"Febrero", 2:"Marzo", 3:"Abril", 4:"Mayo", 5:"Junio",
  6:"Julio", 7:"Agosto", 8:"Septiembre", 9:"Octubre", 10:"Noviembre", 11:"Diciembre"
};

// ─── Calcular todos los datos del reporte ─────────────────────────────────────
function calcularDatos(rows) {
  const desvios = rows.filter(isDesvio);
  const total   = rows.length;
  const nDev    = desvios.length;
  const tasa    = pct(nDev, total);

  // Tendencia mensual
  const porMes = {};
  rows.forEach(r => {
    const d = parseDate(r["Fecha"]);
    if (!d) return;
    const key = `${MESES_ES[d.getMonth()]} ${d.getFullYear()}`;
    const mesNum = d.getMonth();
    if (!porMes[key]) porMes[key] = { label: key, mesNum, total: 0, desvios: 0 };
    porMes[key].total++;
    if (isDesvio(r)) porMes[key].desvios++;
  });
  const tendencia = Object.values(porMes).sort((a, b) => {
    if (a.mesNum !== b.mesNum) return a.mesNum - b.mesNum;
    return 0;
  });

  // Por sector
  const porSector = {};
  rows.forEach(r => {
    const s = r["Sector"] || "Sin sector";
    if (!porSector[s]) porSector[s] = { total: 0, desvios: 0, motivos: {} };
    porSector[s].total++;
    if (isDesvio(r)) {
      porSector[s].desvios++;
      const m = clasificarMotivo(r);
      porSector[s].motivos[m] = (porSector[s].motivos[m] || 0) + 1;
    }
  });
  const sectores = Object.entries(porSector)
    .map(([sec, d]) => ({ sector: sec, ...d, pct: pct(d.desvios, d.total) }))
    .sort((a, b) => b.pct - a.pct);

  // Por turno
  const porTurno = {};
  rows.forEach(r => {
    const t = r["Turno"] || "Sin turno";
    if (!porTurno[t]) porTurno[t] = { total: 0, desvios: 0, motivos: {} };
    porTurno[t].total++;
    if (isDesvio(r)) {
      porTurno[t].desvios++;
      const m = clasificarMotivo(r);
      porTurno[t].motivos[m] = (porTurno[t].motivos[m] || 0) + 1;
    }
  });
  const turnos = Object.entries(porTurno)
    .map(([t, d]) => ({ turno: t, ...d, pct: pct(d.desvios, d.total) }))
    .sort((a, b) => b.pct - a.pct);

  // Top 5 delegados
  const porDel = {};
  rows.forEach(r => {
    const n = r["Nombre y Apellido"];
    if (!porDel[n]) porDel[n] = { nombre: n, sector: r["Sector"], turno: r["Turno"], total: 0, desvios: 0, motivos: {} };
    porDel[n].total++;
    if (isDesvio(r)) {
      porDel[n].desvios++;
      const m = clasificarMotivo(r);
      porDel[n].motivos[m] = (porDel[n].motivos[m] || 0) + 1;
    }
  });
  const top5 = Object.values(porDel)
    .map(d => ({ ...d, pct: pct(d.desvios, d.total) }))
    .sort((a, b) => b.desvios - a.desvios)
    .slice(0, 5);

  // Motivos globales
  const motivosGlobal = {};
  desvios.forEach(r => {
    const m = clasificarMotivo(r);
    motivosGlobal[m] = (motivosGlobal[m] || 0) + 1;
  });
  const motivosGlobalArr = Object.entries(motivosGlobal)
    .map(([m, c]) => ({ motivo: m, cant: c, pct: pct(c, nDev) }))
    .sort((a, b) => b.cant - a.cant);

  // LLT
  const lltRows = desvios.filter(r => clasificarMotivo(r) === "LLT / Charla");
  const porDelLLT = {};
  lltRows.forEach(r => {
    const n = r["Nombre y Apellido"];
    if (!porDelLLT[n]) porDelLLT[n] = { nombre: n, sector: r["Sector"], turno: r["Turno"], cant: 0 };
    porDelLLT[n].cant++;
  });
  const lltTop = Object.values(porDelLLT).sort((a, b) => b.cant - a.cant);

  return { total, nDev, tasa, tendencia, sectores, turnos, top5, motivosGlobal: motivosGlobalArr, lltRows, lltTop };
}

// ─── Determinar período ────────────────────────────────────────────────────────
function periodoLabel(rows, desde, hasta) {
  if (desde && hasta) {
    return `${desde.toLocaleDateString("es-AR")} – ${hasta.toLocaleDateString("es-AR")}`;
  }
  const fechas = rows.map(r => parseDate(r["Fecha"])).filter(Boolean).sort((a,b) => a-b);
  if (!fechas.length) return "Período completo";
  const f0 = fechas[0], f1 = fechas[fechas.length-1];
  return `${MESES_ES[f0.getMonth()]} ${f0.getFullYear()} – ${MESES_ES[f1.getMonth()]} ${f1.getFullYear()}`;
}

// ─── GENERAR PPTX ────────────────────────────────────────────────────────────
async function generarReporte(csvPath, desdeStr, hastaStr, outputPath) {
  // Parsear fechas de filtro
  let desde = desdeStr ? parseDate(desdeStr) : null;
  let hasta = hastaStr ? parseDate(hastaStr) : null;
  if (hasta) hasta.setHours(23, 59, 59);

  const todosRows = parseCSV(csvPath);
  const rows = filterByDate(todosRows, desde, hasta);

  if (rows.length === 0) {
    console.error("❌ No hay registros en el período indicado.");
    process.exit(1);
  }

  const D = calcularDatos(rows);
  const periodo = periodoLabel(rows, desde, hasta);
  const nDelegados = new Set(rows.map(r => r["Legajo"])).size;

  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "Movilidad Gremial — Toyota Argentina";

  // ═══════════════════════════════════════════════════
  // SLIDE 1 — PORTADA
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0, y: 4.2, w: 10, h: 1.425, fill: { color: C.blue }, line: { color: C.blue }
    });
    s.addText("GESTIÓN DE PRESENCIA Y MOVILIDAD GREMIAL", {
      x: 0.6, y: 0.7, w: 8.8, h: 0.7, fontSize: 24, bold: true, color: C.white,
      fontFace: "Calibri", align: "center"
    });
    s.addText("Análisis — Evolución del Proceso", {
      x: 0.6, y: 1.55, w: 8.8, h: 0.45, fontSize: 16, color: "A8BFFF",
      fontFace: "Calibri", align: "center", italic: true
    });
    s.addShape(pres.shapes.LINE, {
      x: 3.5, y: 2.2, w: 3, h: 0, line: { color: C.orange, width: 2 }
    });
    s.addText(`Período: ${periodo}  |  ${nDelegados} Delegados  |  2 hs de Movilidad Gremial`, {
      x: 0.6, y: 2.35, w: 8.8, h: 0.4, fontSize: 11, color: "A8BFFF",
      fontFace: "Calibri", align: "center"
    });
    s.addText("Toyota Argentina S.A.", {
      x: 0.6, y: 4.3, w: 8.8, h: 0.35, fontSize: 11, color: C.white,
      fontFace: "Calibri", align: "center", bold: true
    });
    s.addText("Recursos Humanos — Relaciones Laborales", {
      x: 0.6, y: 4.65, w: 8.8, h: 0.3, fontSize: 9, color: "A8BFFF",
      fontFace: "Calibri", align: "center"
    });
    s.addNotes(`Portada del reporte de Movilidad Gremial. Período: ${periodo}. ${nDelegados} delegados analizados.`);
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 2 — INDICADORES CLAVE
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Contexto — Indicadores Claves", periodo);

    // Semana con más desvíos
    const porSemana = {};
    rows.forEach(r => {
      const d = parseDate(r["Fecha"]);
      if (!d || !isDesvio(r)) return;
      const lun = new Date(d);
      lun.setDate(d.getDate() - d.getDay() + 1);
      const key = lun.toLocaleDateString("es-AR");
      porSemana[key] = (porSemana[key] || 0) + 1;
    });
    const semanaPico = Object.entries(porSemana).sort((a,b) => b[1]-a[1])[0];

    const cards = [
      { label: "Registros Analizados", value: D.total.toLocaleString("es-AR"), sub: periodo, color: C.blue },
      { label: "Total de Desvíos", value: D.nDev.toLocaleString("es-AR"), sub: semanaPico ? `Pico: sem. ${semanaPico[0]}` : "", color: C.red },
      { label: "Tasa de Desvío Global", value: fmt_pct(D.tasa), sub: `sobre ${D.total} registros`, color: D.tasa > 15 ? C.red : D.tasa > 10 ? C.orange : C.green },
      { label: "Registros Cumple", value: (D.total - D.nDev).toLocaleString("es-AR"), sub: fmt_pct(100 - D.tasa) + " del total", color: C.green },
    ];
    const cardW = 2.1, cardH = 1.3, gap = 0.2;
    const startX = (10 - (cards.length * cardW + (cards.length - 1) * gap)) / 2;
    cards.forEach((c, i) => {
      kpiCard(pres, s, startX + i * (cardW + gap), 1.1, cardW, cardH, c.label, c.value, c.sub, c.color);
    });

    // Mini barra de tendencia
    if (D.tendencia.length > 0) {
      s.addText("TENDENCIA MENSUAL DE DESVÍOS (%)", {
        x: 0.4, y: 2.65, w: 9.2, h: 0.28, fontSize: 9, bold: true, color: C.navy,
        fontFace: "Calibri", charSpacing: 1
      });
      s.addChart(pres.charts.BAR, [{
        name: "% Desvío",
        labels: D.tendencia.map(t => t.label.split(" ")[0]),
        values: D.tendencia.map(t => parseFloat(pct(t.desvios, t.total).toFixed(1)))
      }], {
        x: 0.4, y: 2.95, w: 9.2, h: 2.4, barDir: "col",
        chartColors: D.tendencia.map(t => {
          const p = pct(t.desvios, t.total);
          return p >= 20 ? C.red : p >= 12 ? C.orange : C.green;
        }),
        chartArea: { fill: { color: C.white }, roundedCorners: false },
        catAxisLabelColor: C.gray, valAxisLabelColor: C.gray,
        valGridLine: { color: C.grayBorder, size: 0.5 }, catGridLine: { style: "none" },
        showValue: true, dataLabelColor: C.black,
        showLegend: false, showTitle: false,
        valAxisMaxVal: 30,
      });
    }
    s.addNotes(`Total registros: ${D.total}. Desvíos: ${D.nDev} (${fmt_pct(D.tasa)}). Período: ${periodo}.`);
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 3 — TENDENCIA MENSUAL
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Tendencia Mensual de Desvíos", periodo);

    if (D.tendencia.length > 0) {
      // Gráfico grande
      s.addChart(pres.charts.LINE, [{
        name: "% Desvío",
        labels: D.tendencia.map(t => t.label.split(" ")[0]),
        values: D.tendencia.map(t => parseFloat(pct(t.desvios, t.total).toFixed(1)))
      }], {
        x: 0.4, y: 1.1, w: 5.5, h: 4.2,
        lineSize: 3, lineSmooth: false,
        chartColors: [C.blue],
        chartArea: { fill: { color: C.white } },
        catAxisLabelColor: C.gray, valAxisLabelColor: C.gray,
        valGridLine: { color: C.grayBorder, size: 0.5 }, catGridLine: { style: "none" },
        showValue: true, dataLabelColor: C.black,
        showLegend: false, showTitle: false,
        valAxisMaxVal: 30,
      });

      // Cards de cada mes a la derecha
      const cardH2 = (4.2 - (D.tendencia.length - 1) * 0.12) / D.tendencia.length;
      D.tendencia.forEach((t, i) => {
        const p = pct(t.desvios, t.total);
        const color = p >= 20 ? C.red : p >= 12 ? C.orange : C.green;
        const bg = p >= 20 ? C.redLight : p >= 12 ? C.orangeLight : C.greenLight;
        const yPos = 1.1 + i * (cardH2 + 0.12);
        s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
          x: 6.2, y: yPos, w: 3.4, h: cardH2, fill: { color: bg },
          line: { color: color, width: 1 }, rectRadius: 0.06
        });
        s.addText(`${t.label.split(" ")[0].toUpperCase()}  ${fmt_pct(p)}`, {
          x: 6.35, y: yPos + 0.05, w: 3.1, h: cardH2 * 0.45,
          fontSize: 11, bold: true, color: color, fontFace: "Calibri"
        });
        s.addText(`${t.desvios} desvíos de ${t.total} registros`, {
          x: 6.35, y: yPos + cardH2 * 0.45, w: 3.1, h: cardH2 * 0.45,
          fontSize: 8.5, color: C.gray, fontFace: "Calibri"
        });
      });
    } else {
      s.addText("No hay suficientes datos para mostrar tendencia mensual.", {
        x: 0.5, y: 2.5, w: 9, h: 1, fontSize: 14, color: C.gray, align: "center"
      });
    }
    s.addNotes("Tendencia mensual de desvíos. Rojo = crítico (≥20%), naranja = elevado (≥12%), verde = normal (<12%).");
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 4 — DESVÍOS POR SECTOR (tabla)
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Desvíos por Sector", periodo);

    // Tabla
    const headers = [
      [
        { text: "Sector", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 10, fontFace: "Calibri", align: "left" } },
        { text: "Registros", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 10, fontFace: "Calibri", align: "center" } },
        { text: "Desvíos", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 10, fontFace: "Calibri", align: "center" } },
        { text: "% Desvío", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 10, fontFace: "Calibri", align: "center" } },
        { text: "Nivel", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 10, fontFace: "Calibri", align: "center" } },
      ]
    ];
    const dataRows = D.sectores.map(sec => {
      const nivel = sec.pct >= 15 ? "Alto" : sec.pct >= 10 ? "Medio" : "Bajo";
      const fillColor = sec.pct >= 15 ? "FEE2E2" : sec.pct >= 10 ? "FEF3C7" : "DCFCE7";
      const textColor = sec.pct >= 15 ? C.red : sec.pct >= 10 ? C.orange : C.green;
      return [
        { text: sec.sector, options: { fontSize: 9.5, fontFace: "Calibri", align: "left" } },
        { text: String(sec.total), options: { fontSize: 9.5, fontFace: "Calibri", align: "center" } },
        { text: String(sec.desvios), options: { fontSize: 9.5, fontFace: "Calibri", align: "center" } },
        { text: fmt_pct(sec.pct), options: { fontSize: 10, fontFace: "Calibri", align: "center", bold: true, color: textColor } },
        { text: nivel, options: { fontSize: 9, fontFace: "Calibri", align: "center", fill: { color: fillColor }, color: textColor, bold: true } },
      ];
    });
    const totalRow = [
      { text: "TOTAL GENERAL", options: { fill: { color: "F1F5F9" }, bold: true, fontSize: 9.5, fontFace: "Calibri" } },
      { text: String(D.total), options: { fill: { color: "F1F5F9" }, bold: true, fontSize: 9.5, fontFace: "Calibri", align: "center" } },
      { text: String(D.nDev), options: { fill: { color: "F1F5F9" }, bold: true, fontSize: 9.5, fontFace: "Calibri", align: "center" } },
      { text: fmt_pct(D.tasa), options: { fill: { color: "F1F5F9" }, bold: true, fontSize: 9.5, fontFace: "Calibri", align: "center" } },
      { text: "", options: { fill: { color: "F1F5F9" } } },
    ];

    s.addTable([...headers, ...dataRows, totalRow], {
      x: 0.35, y: 1.0, w: 9.3, colW: [3.4, 1.4, 1.2, 1.3, 2.0],
      border: { pt: 0.5, color: C.grayBorder },
      rowH: 0.33,
      autoPage: false,
    });

    // leyenda
    const leyenda = [
      { lbl: "Alto (≥15%)", bg: "FEE2E2", c: C.red },
      { lbl: "Medio (10–14.9%)", bg: "FEF3C7", c: C.orange },
      { lbl: "Bajo (<10%)", bg: "DCFCE7", c: C.green },
    ];
    leyenda.forEach((l, i) => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.35 + i * 3.1, y: 5.22, w: 2.8, h: 0.25,
        fill: { color: l.bg }, line: { color: l.c, width: 0.5 }, rectRadius: 0.04
      });
      s.addText(l.lbl, {
        x: 0.35 + i * 3.1, y: 5.22, w: 2.8, h: 0.25,
        fontSize: 8.5, color: l.c, fontFace: "Calibri", align: "center", bold: true
      });
    });
    s.addNotes("Desvíos por sector. Los más críticos son los que superan el 15% de tasa.");
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 5 — MOTIVOS POR SECTOR (top 6 críticos)
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Motivos por Sector — Perfil de desvíos en los 6 sectores más críticos", periodo);

    const top6Sec = D.sectores.slice(0, 6);
    const colW = 3.0, colH = 1.82, gapX = 0.2, gapY = 0.18;
    const startX = (10 - 2 * colW - gapX) / 2;

    top6Sec.forEach((sec, i) => {
      const col = i % 2, row = Math.floor(i / 3) + (i % 3 >= 0 ? Math.floor(i / 3) : 0);
      // 2 columnas x 3 filas but let me do 3 cols x 2 rows
      const c = i % 3, r = Math.floor(i / 3);
      const x = 0.25 + c * (3.15 + 0.1);
      const y = 1.0 + r * (colH + gapY);

      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y, w: 3.15, h: colH, fill: { color: C.grayLight },
        line: { color: C.grayBorder, width: 0.5 }, shadow: makeShadow(), rectRadius: 0.07
      });

      const pctSec = sec.pct;
      const color = pctSec >= 15 ? C.red : pctSec >= 10 ? C.orange : C.green;
      s.addText(`${sec.sector}   ${fmt_pct(pctSec)} desvío`, {
        x: x + 0.1, y: y + 0.07, w: 2.95, h: 0.28,
        fontSize: 8.5, bold: true, color: color, fontFace: "Calibri"
      });

      const motivos = Object.entries(sec.motivos).sort((a, b) => b[1] - a[1]).slice(0, 4);
      motivos.forEach(([mot, cant], mi) => {
        const pctMot = pct(cant, sec.desvios);
        // barra de progreso
        const barW = 2.0;
        const filledW = barW * (pctMot / 100);
        s.addShape(pres.shapes.RECTANGLE, {
          x: x + 0.1, y: y + 0.38 + mi * 0.33, w: barW, h: 0.08,
          fill: { color: C.grayBorder }, line: { color: C.grayBorder }
        });
        if (filledW > 0) {
          s.addShape(pres.shapes.RECTANGLE, {
            x: x + 0.1, y: y + 0.38 + mi * 0.33, w: filledW, h: 0.08,
            fill: { color: color }, line: { color: color }
          });
        }
        // Etiqueta corta
        const motCorto = mot.replace("Movilización / Actividad Gremial", "Movilización Gremial")
                           .replace("Exceso en Movilidad Gremial (tiempo)", "Exceso MG (tiempo)")
                           .replace("Ausencia / Licencia Médica o ART", "Lic. Médica/ART")
                           .replace("Incumplimiento / Ausencia sin justificar", "Incumplimiento")
                           .replace("Actividad Gremial (otras)", "Act. Gremial otras");
        s.addText(`${motCorto}  ${fmt_pct(pctMot)}`, {
          x: x + 0.1, y: y + 0.47 + mi * 0.33, w: 2.95, h: 0.22,
          fontSize: 7.5, color: C.black, fontFace: "Calibri"
        });
      });
    });
    s.addNotes("Motivos de desvío por sector, para los 6 sectores más críticos.");
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 6 — DESVÍOS POR TURNO
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Desvíos por Turno", periodo);

    s.addChart(pres.charts.BAR, [{
      name: "% Desvío",
      labels: D.turnos.map(t => t.turno),
      values: D.turnos.map(t => parseFloat(pct(t.desvios, t.total).toFixed(1)))
    }], {
      x: 0.4, y: 1.05, w: 4.5, h: 4.3, barDir: "bar",
      chartColors: D.turnos.map(t => {
        const p = pct(t.desvios, t.total);
        return p >= 15 ? C.red : p >= 10 ? C.orange : C.green;
      }),
      chartArea: { fill: { color: C.white } },
      catAxisLabelColor: C.gray, valAxisLabelColor: C.gray,
      valGridLine: { color: C.grayBorder, size: 0.5 }, catGridLine: { style: "none" },
      showValue: true, dataLabelColor: C.black, dataLabelFontSize: 10,
      showLegend: false, showTitle: false,
    });

    // Cards de motivos por turno
    const turnosMostrar = D.turnos.slice(0, 5);
    const cardH3 = (4.3 - (turnosMostrar.length - 1) * 0.1) / turnosMostrar.length;
    turnosMostrar.forEach((t, i) => {
      const p = pct(t.desvios, t.total);
      const color = p >= 15 ? C.red : p >= 10 ? C.orange : C.green;
      const bg = p >= 15 ? C.redLight : p >= 10 ? C.orangeLight : C.greenLight;
      const yy = 1.05 + i * (cardH3 + 0.1);
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 5.1, y: yy, w: 4.6, h: cardH3, fill: { color: bg },
        line: { color: color, width: 0.5 }, rectRadius: 0.06
      });
      s.addText(`TURNO ${t.turno}   ${fmt_pct(p)}`, {
        x: 5.2, y: yy + 0.04, w: 4.35, h: 0.25,
        fontSize: 9.5, bold: true, color: color, fontFace: "Calibri"
      });
      const motivos = Object.entries(t.motivos).sort((a, b) => b[1] - a[1]).slice(0, 3);
      motivos.forEach(([mot, cant], mi) => {
        const pm = pct(cant, t.desvios);
        const mc = mot.replace("Movilización / Actividad Gremial", "Movilización Gremi.")
                      .replace("Exceso en Movilidad Gremial (tiempo)", "Exceso MG")
                      .replace("Ausencia / Licencia Médica o ART", "Lic. Médica/ART")
                      .replace("Incumplimiento / Ausencia sin justificar", "Incumplimiento")
                      .replace("Actividad Gremial (otras)", "Act. Gremial otras");
        s.addText(`${mc}  ${fmt_pct(pm)}`, {
          x: 5.2, y: yy + 0.29 + mi * 0.22, w: 4.35, h: 0.2,
          fontSize: 8, color: C.black, fontFace: "Calibri"
        });
      });
    });
    s.addNotes("Desvíos por turno. El turno con mayor tasa concentra más riesgo.");
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 7 — TOP 5 DELEGADOS
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Top 5 Delegados con Mayor Índice de Desvíos", periodo);

    const colors5 = [C.red, C.purple, C.orange, C.blue, C.green];
    const cardW5 = 1.7, cardH5 = 3.8;
    const startX5 = (10 - 5 * cardW5 - 4 * 0.1) / 2;

    D.top5.forEach((del, i) => {
      const color = colors5[i];
      const x5 = startX5 + i * (cardW5 + 0.1);
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: x5, y: 1.05, w: cardW5, h: cardH5, fill: { color: C.white },
        line: { color: C.grayBorder, width: 1 }, shadow: makeShadow(), rectRadius: 0.08
      });
      // número ranking
      s.addShape(pres.shapes.OVAL, {
        x: x5 + cardW5 / 2 - 0.22, y: 1.12, w: 0.44, h: 0.44,
        fill: { color: color }, line: { color: color }
      });
      s.addText(`#${i + 1}`, {
        x: x5 + cardW5 / 2 - 0.22, y: 1.12, w: 0.44, h: 0.44,
        fontSize: 11, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle"
      });
      // nombre
      const apellido = del.nombre.split(" ").slice(-2).join(" ");
      s.addText(apellido, {
        x: x5 + 0.08, y: 1.62, w: cardW5 - 0.16, h: 0.42,
        fontSize: 9.5, bold: true, color: C.black, fontFace: "Calibri", align: "center"
      });
      s.addText(del.sector.replace(" Division", ""), {
        x: x5 + 0.08, y: 2.0, w: cardW5 - 0.16, h: 0.28,
        fontSize: 7.5, color: C.gray, fontFace: "Calibri", align: "center"
      });
      // desvíos
      s.addText(String(del.desvios), {
        x: x5 + 0.08, y: 2.3, w: cardW5 - 0.16, h: 0.52,
        fontSize: 30, bold: true, color: color, fontFace: "Calibri", align: "center"
      });
      s.addText("desvíos", {
        x: x5 + 0.08, y: 2.78, w: cardW5 - 0.16, h: 0.22,
        fontSize: 8, color: C.gray, fontFace: "Calibri", align: "center"
      });
      s.addText(fmt_pct(del.pct), {
        x: x5 + 0.08, y: 3.0, w: cardW5 - 0.16, h: 0.26,
        fontSize: 11, bold: true, color: color, fontFace: "Calibri", align: "center"
      });
      // top motivo
      const topMot = Object.entries(del.motivos).sort((a,b) => b[1]-a[1])[0];
      if (topMot) {
        const mc = topMot[0].replace("Movilización / Actividad Gremial", "Movilización")
                             .replace("Exceso en Movilidad Gremial (tiempo)", "Exceso MG")
                             .replace("Ausencia / Licencia Médica o ART", "Lic. Médica/ART")
                             .replace("Incumplimiento / Ausencia sin justificar", "Incumplimiento");
        s.addText(`Principal:\n${mc}`, {
          x: x5 + 0.08, y: 3.3, w: cardW5 - 0.16, h: 0.55,
          fontSize: 7.5, color: C.gray, fontFace: "Calibri", align: "center"
        });
      }
    });
    s.addNotes(`Top 5 delegados con más desvíos en el período. Ranking por cantidad absoluta.`);
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 8 — FOCALIZAR EL PROBLEMA
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Focalizar el Problema", periodo);

    const movGlobal = D.motivosGlobal.find(m => m.motivo === "Movilización / Actividad Gremial");
    const pctMov = movGlobal ? movGlobal.pct : 0;
    const sectoresAltos = D.sectores.filter(s => s.pct >= 15).length;
    const atipicos = D.top5.filter(d => {
      const lic = d.motivos["Ausencia / Licencia Médica o ART"] || 0;
      return lic / d.desvios > 0.3;
    });

    const bloques = [
      {
        icono: "🌐", tipo: "HOMOGÉNEO\n(Transversal)", color: C.blue, bg: C.blueLight,
        titulo: "Institucional",
        texto: `La Movilización / Actividad Gremial (${fmt_pct(pctMov)}) afecta a los ${D.sectores.length} sectores y domina en la mayoría.\nNo se puede resolver — requiere decisión política.`,
        stat: `${sectoresAltos} / ${D.sectores.length}\nsectores afectados`,
      },
      {
        icono: "🎯", tipo: "FOCALIZADO\n(Por sector)", color: C.orange, bg: C.orangeLight,
        titulo: "Operativo",
        texto: `Exceso MG → ${D.sectores.slice(0,2).map(s => `${s.sector.replace(" Division","")} (${fmt_pct(pct((s.motivos["Exceso en Movilidad Gremial (tiempo)"]||0), s.desvios))})`).join(" y ")}\nEstos SÍ son abordables.`,
        stat: `${Math.min(3, sectoresAltos)} sectores\nmás afectados`,
      },
      {
        icono: "👤", tipo: "FOCALIZADO\n(Por persona)", color: C.red, bg: C.redLight,
        titulo: "Individuales",
        texto: atipicos.length > 0
          ? `${atipicos.map(d=>d.nombre.split(" ").slice(-1)[0]).join(" y ")} tienen perfiles ATÍPICOS: dominados por ausentismo médico.\nSon casos para seguir con Medicina del Trabajo.`
          : `Los delegados del Top 5 tienen perfiles diferenciados que requieren seguimiento individual.`,
        stat: `${atipicos.length || D.top5.length} delegados\ncríticos`,
      },
    ];

    bloques.forEach((b, i) => {
      const x = 0.3 + i * 3.2;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.0, w: 3.1, h: 4.35, fill: { color: b.bg },
        line: { color: b.color, width: 1.5 }, shadow: makeShadow(), rectRadius: 0.1
      });
      s.addText(b.icono, {
        x, y: 1.1, w: 3.1, h: 0.5, fontSize: 22, align: "center"
      });
      s.addText(b.tipo, {
        x: x + 0.1, y: 1.55, w: 2.9, h: 0.55,
        fontSize: 10, bold: true, color: b.color, fontFace: "Calibri", align: "center"
      });
      s.addText(b.titulo, {
        x: x + 0.1, y: 2.1, w: 2.9, h: 0.3,
        fontSize: 9, color: C.gray, fontFace: "Calibri", align: "center", italic: true
      });
      s.addShape(pres.shapes.LINE, {
        x: x + 0.5, y: 2.42, w: 2.1, h: 0, line: { color: b.color, width: 0.75 }
      });
      s.addText(b.texto, {
        x: x + 0.12, y: 2.5, w: 2.86, h: 1.35,
        fontSize: 8.5, color: C.black, fontFace: "Calibri", wrap: true
      });
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: x + 0.3, y: 3.9, w: 2.5, h: 0.6,
        fill: { color: b.color }, line: { color: b.color }, rectRadius: 0.06
      });
      s.addText(b.stat, {
        x: x + 0.3, y: 3.9, w: 2.5, h: 0.6,
        fontSize: 9.5, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle"
      });
    });
    s.addNotes("Clasificación del problema en tres categorías: homogéneo (institucional), focalizado por sector (operativo) y focalizado por persona (individual).");
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 9 — MOTIVOS GLOBALES vs TOP 5
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Análisis entre Motivos Globales con el Top 5", periodo);

    // Columna izquierda: motivos globales
    s.addText("GLOBAL", {
      x: 0.3, y: 1.05, w: 3.7, h: 0.28, fontSize: 9, bold: true, color: C.navy,
      fontFace: "Calibri", charSpacing: 1
    });
    s.addText(`(${D.nDev} desvíos)`, {
      x: 0.3, y: 1.3, w: 3.7, h: 0.2, fontSize: 8, color: C.gray, fontFace: "Calibri"
    });

    D.motivosGlobal.slice(0, 7).forEach((m, i) => {
      const barMaxW = 3.3;
      const filledW = barMaxW * (m.pct / 100);
      const yy = 1.55 + i * 0.52;
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.3, y: yy, w: barMaxW, h: 0.18,
        fill: { color: C.grayBorder }, line: { color: C.grayBorder }
      });
      if (filledW > 0.01) {
        s.addShape(pres.shapes.RECTANGLE, {
          x: 0.3, y: yy, w: filledW, h: 0.18,
          fill: { color: C.blue }, line: { color: C.blue }
        });
      }
      const mc = m.motivo.replace("Movilización / Actividad Gremial", "Movilización")
                         .replace("Exceso en Movilidad Gremial (tiempo)", "Exceso MG")
                         .replace("Ausencia / Licencia Médica o ART", "Lic. Médica/ART")
                         .replace("Incumplimiento / Ausencia sin justificar", "Incumplimiento")
                         .replace("Actividad Gremial (otras)", "Act. Gremial otras");
      s.addText(`${fmt_pct(m.pct)}  ${mc}`, {
        x: 0.3, y: yy + 0.19, w: 3.7, h: 0.26,
        fontSize: 8.5, color: C.black, fontFace: "Calibri"
      });
    });

    // Columna derecha: top5 perfil
    const colors5 = [C.red, C.purple, C.orange, C.blue, C.green];
    const atipIconos = ["⚠️", "⚠️", "MIX", "✅", "✅"];
    D.top5.forEach((del, i) => {
      const color = colors5[i];
      const yy = 1.05 + i * 0.87;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 4.35, y: yy, w: 5.3, h: 0.78,
        fill: { color: C.grayLight }, line: { color: C.grayBorder, width: 0.5 }, rectRadius: 0.06
      });
      const topMot = Object.entries(del.motivos).sort((a,b)=>b[1]-a[1])[0];
      const topPct = topMot ? fmt_pct(pct(topMot[1], del.desvios)) : "";
      const mc = topMot ? topMot[0].replace("Movilización / Actividad Gremial", "Movilización Gremial")
                                    .replace("Exceso en Movilidad Gremial (tiempo)", "Exceso MG (tiempo)")
                                    .replace("Ausencia / Licencia Médica o ART", "Médico/ART")
                                    .replace("Incumplimiento / Ausencia sin justificar", "Incumplimiento") : "";
      s.addText(`${atipIconos[i]}  ${del.nombre}`, {
        x: 4.5, y: yy + 0.06, w: 4, h: 0.25, fontSize: 9.5, bold: true, color: color, fontFace: "Calibri"
      });
      s.addText(`${topPct} ${mc}`, {
        x: 4.5, y: yy + 0.3, w: 5.0, h: 0.22, fontSize: 8.5, color: C.black, fontFace: "Calibri"
      });
      s.addText(`${del.desvios} desvíos — ${fmt_pct(del.pct)}`, {
        x: 4.5, y: yy + 0.52, w: 5.0, h: 0.2, fontSize: 8, color: C.gray, fontFace: "Calibri"
      });
    });
    s.addNotes("Comparación entre el perfil global de desvíos y el perfil individual del Top 5.");
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 10 — LLT / CHARLA 5 (resumen)
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "LLT / Charla 5' / Extensiones — Análisis global", periodo);

    const nLLT = D.lltRows.length;
    const nDelLLT = new Set(D.lltRows.map(r => r["Nombre y Apellido"])).size;
    const pctLLTtot = pct(nLLT, D.total);
    const pctLLTdev = pct(nLLT, D.nDev);

    const kpis = [
      { label: "Total Desvíos LLT/Extensiones", value: String(nLLT), color: C.orange },
      { label: "% sobre total registros", value: fmt_pct(pctLLTtot), color: C.blue },
      { label: "% sobre total desvíos", value: fmt_pct(pctLLTdev), color: C.red },
      { label: `Delegados afectados`, value: `${nDelLLT}/${nDelegados}`, color: C.purple },
    ];
    kpis.forEach((k, i) => {
      kpiCard(pres, s, 0.3 + i * 2.35, 1.05, 2.15, 1.2, k.label, k.value, "", k.color);
    });

    // Tabla LLT
    if (D.lltTop.length > 0) {
      s.addText("LLT representa el " + fmt_pct(pctLLTdev) + " del total de desvíos", {
        x: 0.3, y: 2.4, w: 9.4, h: 0.3, fontSize: 10, color: C.gray,
        fontFace: "Calibri", italic: true
      });

      const tableRows = [
        [
          { text: "Delegado", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 9, fontFace: "Calibri" } },
          { text: "Sector", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 9, fontFace: "Calibri" } },
          { text: "Turno", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 9, fontFace: "Calibri", align: "center" } },
          { text: "Desvíos LLT", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 9, fontFace: "Calibri", align: "center" } },
          { text: "% del total", options: { fill: { color: C.navy }, color: C.white, bold: true, fontSize: 9, fontFace: "Calibri", align: "center" } },
        ],
        ...D.lltTop.slice(0, 8).map(d => [
          { text: d.nombre, options: { fontSize: 9, fontFace: "Calibri" } },
          { text: d.sector || "", options: { fontSize: 8.5, fontFace: "Calibri" } },
          { text: d.turno || "", options: { fontSize: 9, fontFace: "Calibri", align: "center" } },
          { text: String(d.cant), options: { fontSize: 9, fontFace: "Calibri", align: "center", bold: true } },
          { text: fmt_pct(pct(d.cant, nLLT)), options: { fontSize: 9, fontFace: "Calibri", align: "center" } },
        ])
      ];
      s.addTable(tableRows, {
        x: 0.3, y: 2.75, w: 9.4, colW: [2.8, 2.5, 1.2, 1.4, 1.5],
        border: { pt: 0.5, color: C.grayBorder }, rowH: 0.3
      });
    }
    s.addNotes(`LLT y charlas de 5': ${nLLT} desvíos (${fmt_pct(pctLLTdev)} del total). Delegados afectados: ${nDelLLT}.`);
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 11 — LLT DETALLE POR DELEGADO (top 5)
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "LLT / Charla 5' / Extensiones — Detalle por delegado", periodo);

    const nLLT = D.lltRows.length;
    const top5LLT = D.lltTop.slice(0, 5);
    const colH4 = (4.3 - (top5LLT.length - 1) * 0.1) / top5LLT.length;

    top5LLT.forEach((d, i) => {
      const yy = 1.05 + i * (colH4 + 0.1);
      const pctDel = pct(d.cant, nLLT);
      const color = i === 0 ? C.red : i === 1 ? C.orange : C.blue;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.3, y: yy, w: 9.4, h: colH4, fill: { color: C.grayLight },
        line: { color: C.grayBorder, width: 0.5 }, rectRadius: 0.06
      });
      s.addShape(pres.shapes.OVAL, {
        x: 0.38, y: yy + (colH4 - 0.45) / 2, w: 0.45, h: 0.45,
        fill: { color: color }, line: { color: color }
      });
      s.addText(`#${i + 1}`, {
        x: 0.38, y: yy + (colH4 - 0.45) / 2, w: 0.45, h: 0.45,
        fontSize: 11, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle"
      });
      s.addText(`${d.nombre}  —  ${d.sector || ""}  |  Turno ${d.turno || ""}`, {
        x: 0.93, y: yy + 0.05, w: 6.0, h: 0.28, fontSize: 9.5, bold: true, color: C.black, fontFace: "Calibri"
      });
      s.addText(`${d.cant} desvíos — ${fmt_pct(pct(d.cant, nLLT))} del total LLT`, {
        x: 0.93, y: yy + colH4 - 0.32, w: 6.0, h: 0.25, fontSize: 8, color: C.gray, fontFace: "Calibri"
      });
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 8.15, y: yy + (colH4 - 0.5) / 2, w: 1.35, h: 0.5,
        fill: { color: color }, line: { color: color }, rectRadius: 0.06
      });
      s.addText(`${d.cant} dev.\n${fmt_pct(pctDel)}`, {
        x: 8.15, y: yy + (colH4 - 0.5) / 2, w: 1.35, h: 0.5,
        fontSize: 9.5, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle"
      });
    });

    if (top5LLT.length >= 2) {
      const top2 = pct(top5LLT[0].cant + top5LLT[1].cant, D.lltRows.length);
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.3, y: 5.12, w: 9.4, h: 0.32, fill: { color: C.orangeLight },
        line: { color: C.orange, width: 0.5 }, rectRadius: 0.04
      });
      s.addText(
        `⚠️  ${top5LLT[0].nombre} + ${top5LLT[1].nombre} = ${fmt_pct(top2)} de todos los desvíos LLT. Considerar estos casos para reportar.`,
        { x: 0.45, y: 5.13, w: 9.1, h: 0.28, fontSize: 8.5, color: C.orange, fontFace: "Calibri", bold: true }
      );
    }
    s.addNotes("Detalle de los delegados con más desvíos LLT.");
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 12 — ANÁLISIS FINAL / LECTURA DEL PROBLEMA
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    addSlideHeader(pres, s, "Análisis Final — Lectura del Problema", periodo);

    const bloques12 = [
      {
        titulo: "El proceso de control existe y funciona.",
        texto: `Sin embargo, los desvíos no tienden hacia cero, sino que fluctúan de forma irregular, con picos recurrentes.`,
        color: C.blue
      },
      {
        titulo: "¿Se corrigen los desvíos?",
        texto: `No de forma sostenida. Los mismos delegados y sectores reaparecen con desvíos en distintos meses, lo que indica que las correcciones son temporales.`,
        color: C.orange
      },
      {
        titulo: "Riesgo de no actuar",
        texto: `Sin un seguimiento continuo, se consolida la normalización del desvío. Los delegados y sectores críticos perderán el objetivo principal: "El trabajo de los delegados en la línea".`,
        color: C.red
      },
    ];

    bloques12.forEach((b, i) => {
      const yy = 1.15 + i * 1.35;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.4, y: yy, w: 9.2, h: 1.2, fill: { color: C.grayLight },
        line: { color: b.color, width: 1 }, shadow: makeShadow(), rectRadius: 0.08
      });
      s.addText(b.titulo, {
        x: 0.6, y: yy + 0.1, w: 8.8, h: 0.32,
        fontSize: 11, bold: true, color: b.color, fontFace: "Calibri"
      });
      s.addText(b.texto, {
        x: 0.6, y: yy + 0.42, w: 8.8, h: 0.7,
        fontSize: 10, color: C.black, fontFace: "Calibri", wrap: true
      });
    });
    s.addNotes("Lectura del problema: el proceso funciona pero los desvíos no se corrigen de forma sostenida.");
  }

  // ═══════════════════════════════════════════════════
  // SLIDE 13 — CONCLUSIONES Y PRÓXIMOS PASOS
  // ═══════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addText("CONCLUSIONES Y PRÓXIMOS PASOS", {
      x: 0.5, y: 0.3, w: 9, h: 0.55, fontSize: 20, bold: true, color: C.white,
      fontFace: "Calibri", align: "center", charSpacing: 1
    });
    s.addShape(pres.shapes.LINE, {
      x: 3, y: 0.9, w: 4, h: 0, line: { color: C.orange, width: 2 }
    });

    // Columna conclusiones
    s.addText("CONCLUSIONES", {
      x: 0.4, y: 1.05, w: 5.6, h: 0.3, fontSize: 11, bold: true, color: C.orange,
      fontFace: "Calibri", charSpacing: 1
    });

    const concs = [
      `El proceso de control permitió identificar dónde están los desvíos.`,
      `La tasa global es del ${fmt_pct(D.tasa)} — los desvíos no se corrigen de forma sostenida.`,
      D.tendencia.length > 0 ? `Pico crítico: ${D.tendencia.reduce((a,b) => pct(a.desvios,a.total) > pct(b.desvios,b.total) ? a : b).label} (${fmt_pct(pct(D.tendencia.reduce((a,b)=>pct(a.desvios,a.total)>pct(b.desvios,b.total)?a:b).desvios, D.tendencia.reduce((a,b)=>pct(a.desvios,a.total)>pct(b.desvios,b.total)?a:b).total))}).` : `Tendencia irregular con picos en algunos meses.`,
      `El turno ${D.turnos[0]?.turno || ""} concentra el mayor porcentaje de desvíos (${fmt_pct(D.turnos[0]?.pct || 0)}).`,
      `Los sectores ${D.sectores.slice(0,3).map(s=>s.sector.replace(" Division","")).join(", ")} concentran el riesgo más alto.`,
      `Los 3 delegados del Top 3 superan el ${fmt_pct(D.top5[2]?.pct || 0)} individual — sin corrección visible.`,
    ];

    s.addText(concs.map(c => ({ text: `✓  ${c}`, options: { bullet: false, breakLine: true } })), {
      x: 0.4, y: 1.38, w: 5.6, h: 3.8, fontSize: 8.5, color: "CADCFC",
      fontFace: "Calibri", wrap: true, valign: "top"
    });

    // Columna próximos pasos
    s.addText("PRÓXIMOS PASOS", {
      x: 6.3, y: 1.05, w: 3.4, h: 0.3, fontSize: 11, bold: true, color: C.orange,
      fontFace: "Calibri", charSpacing: 1
    });

    const pasos = [
      "Reunión con CIR y sectores críticos.",
      "Seguimiento individual de delegados atípicos con SM.",
      "Reportar Campodonico e Iara Lopez por LLT.",
      "Monitoreo semanal de tasa de desvío.",
      "Generar nota de desvío en casos de reincidencia.",
    ];
    pasos.forEach((p, i) => {
      s.addShape(pres.shapes.OVAL, {
        x: 6.3, y: 1.42 + i * 0.66, w: 0.32, h: 0.32,
        fill: { color: C.orange }, line: { color: C.orange }
      });
      s.addText(String(i + 1), {
        x: 6.3, y: 1.42 + i * 0.66, w: 0.32, h: 0.32,
        fontSize: 9, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle"
      });
      s.addText(p, {
        x: 6.7, y: 1.45 + i * 0.66, w: 3.0, h: 0.55,
        fontSize: 8.5, color: "CADCFC", fontFace: "Calibri", wrap: true
      });
    });
    s.addNotes("Conclusiones y próximos pasos del análisis de movilidad gremial.");
  }

  // ─── Guardar ───────────────────────────────────────
  await pres.writeFile({ fileName: outputPath });
  console.log(`✅ PPT generado: ${outputPath}`);
  console.log(`   Período: ${periodo}`);
  console.log(`   Registros: ${D.total} | Desvíos: ${D.nDev} (${fmt_pct(D.tasa)})`);
}

// ─── Entry point ──────────────────────────────────────────────────────────────
const [,, csvPath, desdeStr, hastaStr] = process.argv;
if (!csvPath) {
  console.error("Uso: node generar_reporte.js <registro_gremial.csv> [dd/mm/aaaa] [dd/mm/aaaa]");
  process.exit(1);
}
const outName = `Movilidad_Gremial_${new Date().toLocaleDateString("es-AR").replace(/\//g,"-")}.pptx`;
const outPath = path.join(path.dirname(csvPath), outName);

generarReporte(csvPath, desdeStr, hastaStr, outPath).catch(err => {
  console.error("❌ Error:", err.message);
  process.exit(1);
});
