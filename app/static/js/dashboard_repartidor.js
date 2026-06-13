/* ═══════════════════════════════════════════════════
   Foodly · dashboard_repartidor.js – Premium v3
   Rich gradients · Zone badges · Animated history
   Smart empty-data handling
═══════════════════════════════════════════════════ */

/* ── Helper: show empty state for custom charts ────── */
function mostrarVacio(canvasId, mensaje = "Sin datos disponibles") {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ex = Chart.getChart(canvas);
  if (ex) ex.destroy();
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const parent = canvas.parentElement;
  if (parent) {
    let emptyMsg = parent.querySelector('.chart-empty-msg');
    if (!emptyMsg) {
      emptyMsg = document.createElement('div');
      emptyMsg.className = 'chart-empty-msg';
      emptyMsg.innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;min-height:200px;gap:12px;">
          <i class="fa-solid fa-chart-simple" style="font-size:40px;background:linear-gradient(135deg,#43B0AF,#67FFF2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;opacity:.5;"></i>
          <span style="font-size:13px;color:#94a3b8;font-weight:500;font-family:'Outfit',sans-serif;">${mensaje}</span>
          <span style="font-size:11px;color:#64748b;font-family:'Inter',sans-serif;">Los datos aparecerán aquí cuando estén disponibles</span>
        </div>
      `;
      parent.appendChild(emptyMsg);
    }
    canvas.style.display = 'none';
  }
}

function limpiarVacio(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  canvas.style.display = '';
  const emptyMsg = canvas.parentElement?.querySelector('.chart-empty-msg');
  if (emptyMsg) emptyMsg.remove();
}

function datosValidos(d) {
  return d && d.labels && d.data && d.labels.length > 0 && d.data.length > 0 
    && !d.data.every(v => v === 0 || v === null || v === undefined);
}

/* ── KPIs ─────────────────────────────────────────── */
async function cargarKPIs() {
  const data = await fetchData("/dashboard/api/repartidor/kpis");
  console.log("[Repartidor] kpis:", data);
  if (data) renderKpis("kpis-container", data);
}

/* ── Entregas por día ─────────────────────────────── */
async function cargarDia() {
  const d = await fetchData("/dashboard/api/repartidor/entregas-dia");
  console.log("[Repartidor] entregas-dia:", d);
  if (!d) return;
  crearGrafico("chart-entregas-dia", "line", d.labels, d.data, {
    label: "Entregas",
  });
}

/* ── Entregas por zona ────────────────────────────── */
async function cargarZonas() {
  const d = await fetchData("/dashboard/api/repartidor/entregas-zona");
  console.log("[Repartidor] entregas-zona:", d);
  if (!d) return;
  crearGrafico("chart-zonas", "doughnut", d.labels, d.data);
}

/* ── Historial de entregas (tabla premium) ────────── */
async function cargarHistorial() {
  const data = await fetchData("/dashboard/api/repartidor/historial");
  console.log("[Repartidor] historial:", data);
  if (!data) return;

  const rows = (data.rows || []).map(e => ({
    "#":           `<span style="font-weight:700;color:var(--rojo-claro);font-size:13px;">#${e.id}</span>`,
    "Repartidor":  `<span style="font-weight:500;"><i class="fa-solid fa-user" style="font-size:10px;color:var(--texto-ter);margin-right:4px;"></i>${e.repartidor || "—"}</span>`,
    "Zona":        e.zona && e.zona !== "—"
                     ? `<span style="font-size:11px;background:linear-gradient(135deg,var(--platino),#d4d7db);color:var(--negro);padding:3px 10px;border-radius:12px;font-weight:500;">
                          <i class='fa-solid fa-location-dot' style='font-size:9px;'></i> ${e.zona}</span>`
                     : `<span style="color:var(--texto-ter);">—</span>`,
    "Asignación":  `<span style="font-size:11px;color:var(--texto-sec);">
                      <i class="fa-regular fa-calendar" style="font-size:9px;margin-right:3px;"></i>${e.asignacion || "—"}</span>`,
    "Aceptación":  e.aceptacion && e.aceptacion !== "—"
                     ? `<span style="font-size:11px;color:var(--rojo-claro);font-weight:500;">
                          <i class="fa-solid fa-circle-check" style="font-size:9px;margin-right:3px;"></i>${e.aceptacion}</span>`
                     : `<span style="font-size:11px;color:var(--texto-ter);">—</span>`,
  }));

  renderTabla("tbody-historial", "thead-historial", {
    columns: ["#", "Repartidor", "Zona", "Asignación", "Aceptación"],
    rows,
  });

  initDataTable("tabla-historial");
}

/* ── Disponibilidad de repartidores ───────────────── */
async function cargarVehiculos() {
  const d = await fetchData("/dashboard/api/repartidor/vehiculos-tipo");
  console.log("[Repartidor] vehiculos-tipo:", d);
  if (!d) return;

  // Check for empty/invalid data
  if (!datosValidos(d)) {
    mostrarVacio("chart-vehiculos", "Sin datos de disponibilidad");
    return;
  }
  limpiarVacio("chart-vehiculos");

  const canvas = document.getElementById("chart-vehiculos");
  if (!canvas) return;
  const ex = Chart.getChart(canvas); if (ex) ex.destroy();
  const COLORES = ["rgba(67,176,175,.85)","rgba(42,48,86,.80)","rgba(103,255,242,.75)",
                   "rgba(129,236,134,.75)","rgba(226,91,56,.80)"];
  const BORDERS = ["#43B0AF","#2A3056","#67FFF2","#81EC86","#E25B38"];
  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: d.labels,
      datasets: [{
        data: d.data,
        backgroundColor: COLORES.slice(0, d.labels.length),
        borderColor:     BORDERS.slice(0, d.labels.length),
        borderWidth: 2,
        hoverOffset: 12,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: "62%",
      animation: { duration: 900, easing: "easeOutQuart" },
      plugins: {
        legend: {
          display: true, position: "bottom",
          labels: { usePointStyle: true, pointStyle: "circle", padding: 14,
            font: { size: 11, family: "'Outfit',sans-serif", weight: "500" }, color: "#4a5568" }
        },
        tooltip: {
          backgroundColor: "rgba(30,35,64,.95)", cornerRadius: 10,
          titleFont: { size: 13, weight: "600", family: "'Outfit',sans-serif" },
          bodyFont:  { size: 12, family: "'Inter',sans-serif" },
          padding: { x: 14, y: 10 },
          callbacks: {
            label: (c) => {
              const total = c.dataset.data.reduce((a,b) => a+b, 0);
              const pct = total > 0 ? ((c.parsed / total) * 100).toFixed(1) : 0;
              return `  ${c.parsed} repartidor(es) · ${pct}%`;
            }
          }
        }
      }
    }
  });
}

/* ── Estado de pedidos del repartidor (Polar Area) ── */
async function cargarSemanal() {
  const d = await fetchData("/dashboard/api/repartidor/rendimiento-semanal");
  console.log("[Repartidor] rendimiento-semanal:", d);
  if (!d) return;

  // Check for empty/invalid data
  if (!datosValidos(d)) {
    mostrarVacio("chart-semanal", "Sin datos de estado de pedidos");
    return;
  }
  limpiarVacio("chart-semanal");

  const canvas = document.getElementById("chart-semanal");
  if (!canvas) return;
  const ex = Chart.getChart(canvas); if (ex) ex.destroy();
  const COLORES = [
    "rgba(67,176,175,.80)", "rgba(42,48,86,.75)", "rgba(103,255,242,.70)",
    "rgba(129,236,134,.75)", "rgba(226,91,56,.70)",
  ];
  const BORDERS = ["#43B0AF","#2A3056","#67FFF2","#81EC86","#E25B38"];
  new Chart(canvas, {
    type: "polarArea",
    data: {
      labels: d.labels,
      datasets: [{
        data: d.data,
        backgroundColor: COLORES.slice(0, d.labels.length),
        borderColor:     BORDERS.slice(0, d.labels.length),
        borderWidth: 2,
        hoverBorderWidth: 3,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 900, easing: "easeOutQuart" },
      plugins: {
        legend: {
          display: true, position: "bottom",
          labels: { usePointStyle: true, pointStyle: "circle", padding: 14,
            font: { size: 11, family: "'Outfit',sans-serif", weight: "500" }, color: "#4a5568" }
        },
        tooltip: {
          backgroundColor: "rgba(30,35,64,.95)", cornerRadius: 10,
          titleFont: { size: 13, weight: "600", family: "'Outfit',sans-serif" },
          bodyFont:  { size: 12, family: "'Inter',sans-serif" },
          padding: { x: 14, y: 10 },
          callbacks: {
            label: (c) => {
              const total = c.dataset.data.reduce((a,b) => a+b, 0);
              const pct = total > 0 ? ((c.parsed.r / total) * 100).toFixed(1) : 0;
              return `  ${c.parsed.r} pedido(s) (${pct}%)`;
            }
          }
        }
      },
      scales: {
        r: {
          grid: { color: "rgba(67,176,175,.10)" },
          ticks: { backdropColor: "transparent", color: "#64748b", font: { size: 9 } },
          suggestedMin: 0,
        }
      }
    }
  });
}

/* ── Cargar todo ──────────────────────────────────── */
document.addEventListener("DOMContentLoaded", function () {
  cargarKPIs();
  cargarDia();
  cargarZonas();
  cargarVehiculos();
  cargarSemanal();
  cargarHistorial();
});