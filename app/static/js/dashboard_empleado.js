/* ═══════════════════════════════════════════════════
   Foodly · dashboard_empleado.js – Premium v3
   Rich gradients · Status badges · Smart fallbacks
═══════════════════════════════════════════════════ */

/* ── Helper: empty data handling ────────────────────── */
function _mostrarVacio(canvasId, msg = "Sin datos disponibles") {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ex = Chart.getChart(canvas); if (ex) ex.destroy();
  canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
  const parent = canvas.parentElement;
  if (parent) {
    let em = parent.querySelector('.chart-empty-msg');
    if (!em) {
      em = document.createElement('div');
      em.className = 'chart-empty-msg';
      em.innerHTML = `<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;min-height:200px;gap:12px;"><i class="fa-solid fa-chart-simple" style="font-size:40px;background:linear-gradient(135deg,#43B0AF,#67FFF2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;opacity:.5;"></i><span style="font-size:13px;color:#94a3b8;font-weight:500;font-family:'Outfit',sans-serif;">${msg}</span><span style="font-size:11px;color:#64748b;">Los datos aparecerán aquí cuando estén disponibles</span></div>`;
      parent.appendChild(em);
    }
    canvas.style.display = 'none';
  }
}
function _limpiarVacio(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  canvas.style.display = '';
  const em = canvas.parentElement?.querySelector('.chart-empty-msg');
  if (em) em.remove();
}
function _datosOk(d) {
  return d && d.labels && d.data && d.labels.length > 0 && d.data.length > 0
    && !d.data.every(v => v === 0 || v === null || v === undefined);
}

const ESTADO_BADGE = {
  pendiente:    "estado-pendiente",
  preparacion:  "estado-preparacion",
  "en camino":  "estado-pendiente",
  entregado:    "estado-entregado",
  cancelado:    "estado-cancelado",
};

const ESTADO_ICON = {
  pendiente:    "fa-clock",
  preparacion:  "fa-fire-burner",
  "en camino":  "fa-truck",
  entregado:    "fa-circle-check",
  cancelado:    "fa-circle-xmark",
};

/* ── KPIs ─────────────────────────────────────────── */
async function cargarKPIs() {
  const url = EMP_ID ? `/dashboard/api/empleado/kpis?id=${EMP_ID}` : "/dashboard/api/empleado/kpis";
  const data = await fetchData(url);
  if (data) renderKpis("kpis-container", data);
}

/* ── Estado de pedidos → Polar Area chart ─────────── */
async function cargarEstado() {
  const url = EMP_ID
    ? `/dashboard/api/empleado/pedidos-estado?id=${EMP_ID}`
    : "/dashboard/api/empleado/pedidos-estado";
  const d = await fetchData(url);
  console.log("[Empleado] pedidos-estado:", d);
  if (!d) return;
  if (!_datosOk(d)) { _mostrarVacio("chart-pedidos-estado", "Sin datos de estado"); return; }
  _limpiarVacio("chart-pedidos-estado");

  const canvas = document.getElementById("chart-pedidos-estado");
  if (!canvas) return;
  const existing = Chart.getChart(canvas);
  if (existing) existing.destroy();

  // Paleta del landing: teal, navy, cyan, green, sage, purple
  const COLORES = [
    "rgba(67,176,175,.80)",   // pendiente   → teal
    "rgba(42,48,86,.75)",     // preparacion → navy
    "rgba(103,255,242,.70)",  // en camino   → cyan
    "rgba(129,236,134,.75)",  // entregado   → green
    "rgba(239,68,68,.65)",    // cancelado   → rojo
  ];
  const BORDERS = [
    "#43B0AF", "#2A3056", "#67FFF2", "#81EC86", "#ef4444"
  ];

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
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 900, easing: "easeOutQuart" },
      plugins: {
        legend: {
          display: true,
          position: "bottom",
          labels: {
            usePointStyle: true,
            pointStyle: "circle",
            padding: 16,
            font: { size: 12, family: "'Outfit', sans-serif", weight: "500" },
            color: "#4a5568",
          },
        },
        tooltip: {
          backgroundColor: "rgba(30,35,64,.95)",
          titleFont: { size: 13, weight: "600", family: "'Outfit', sans-serif" },
          bodyFont:  { size: 12, family: "'Inter', sans-serif" },
          padding: { x: 14, y: 10 },
          cornerRadius: 10,
          callbacks: {
            label: (ctx) => {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct   = total > 0 ? ((ctx.parsed.r / total) * 100).toFixed(1) : 0;
              return `  ${ctx.parsed.r} pedidos (${pct}%)`;
            },
          },
        },
      },
      scales: {
        r: {
          grid:       { color: "rgba(67,176,175,.10)" },
          ticks: {
            backdropColor: "transparent",
            color: "#64748b",
            font: { size: 9 },
          },
          suggestedMin: 0,
        },
      },
    },
  });
}

/* ── Productos más vendidos (barra horizontal) ────── */
async function cargarProductos() {
  const url = EMP_ID
    ? `/dashboard/api/empleado/productos-vendidos?id=${EMP_ID}`
    : "/dashboard/api/empleado/productos-vendidos";
  const d = await fetchData(url);
  console.log("[Empleado] productos-vendidos:", d);
  if (!d) return;
  if (!_datosOk(d)) { _mostrarVacio("chart-productos", "Sin datos de productos"); return; }
  _limpiarVacio("chart-productos");

  const canvas = document.getElementById("chart-productos");
  if (!canvas) return;
  const existing = Chart.getChart(canvas);
  if (existing) existing.destroy();

  const ctx = canvas.getContext("2d");

  // Teal palette gradient for each bar
  const barColors = d.data.map((_, i) => {
    const alpha = 1 - (i * 0.07);
    return `rgba(67,176,175,${Math.max(alpha, 0.30)})`;
  });

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: d.labels,
      datasets: [{
        label: "Unidades",
        data: d.data,
        backgroundColor: barColors,
        borderRadius: 6,
        borderSkipped: false,
        barThickness: 20,
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 800, easing: "easeOutQuart" },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(30,35,64,.95)",
          titleFont: { size: 13, weight: "600", family: "'DM Sans'" },
          bodyFont: { size: 12, family: "'DM Sans'" },
          padding: { x: 14, y: 10 },
          cornerRadius: 10,
          callbacks: {
            label: (ctx) => ` ${Number(ctx.parsed.x).toLocaleString("es-BO")} unidades`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(211,209,199,.15)" },
          ticks: { font: { size: 10, weight: "500" }, color: "#888780" },
          border: { display: false },
        },
        y: {
          grid: { display: false },
          ticks: { font: { size: 11, weight: "500" }, color: "#150B08" },
          border: { display: false },
        },
      },
    }
  });
}

/* ── Últimos pedidos (tabla) ──────────────────────── */
async function cargarPedidos() {
  const url = EMP_ID
    ? `/dashboard/api/empleado/ultimos-pedidos?id=${EMP_ID}`
    : "/dashboard/api/empleado/ultimos-pedidos";
  const data = await fetchData(url);
  if (!data) return;

  const rows = (data.rows || []).map(p => {
    const estadoKey = (p.estado || "").toLowerCase();
    const estadoIcon = ESTADO_ICON[estadoKey] || "fa-circle-question";
    return {
      "#":        `<span style="font-weight:700;color:var(--rojo-claro);font-size:13px;">#${p.id_pedido}</span>`,
      "Fecha":    `<span style="font-size:11px;color:var(--texto-sec);">${p.fecha || "—"}</span>`,
      "Cliente":  `<span style="font-weight:500;">${p.cliente || "—"}</span>`,
      "Total":    `<strong style="color:var(--negro);">${p.total || "—"}</strong>`,
      "Método":   p.metodo === "Delivery"
                    ? `<span style="font-size:11px;background:linear-gradient(135deg,var(--platino),#d4d7db);color:var(--negro);padding:3px 10px;border-radius:12px;font-weight:500;">
                        <i class='fa-solid fa-motorcycle' style='font-size:9px;'></i> ${p.metodo}</span>`
                    : `<span style="font-size:11px;color:var(--texto-sec);">${p.metodo || "—"}</span>`,
      "Estado":   `<span class="estado-badge ${ESTADO_BADGE[estadoKey] || "estado-pendiente"}">
                    <i class="fa-solid ${estadoIcon}" style="font-size:9px;"></i> ${p.estado || "—"}</span>`,
    };
  });

  renderTabla("tbody-pedidos", "thead-pedidos", {
    columns: ["#", "Fecha", "Cliente", "Total", "Método", "Estado"],
    rows,
  });

  initDataTable("tabla-pedidos");
}

/* ── Pedidos por tipo de pago (doughnut) ──────────── */
async function cargarHoras() {
  const url = EMP_ID
    ? `/dashboard/api/empleado/tipo-pago?id=${EMP_ID}`
    : "/dashboard/api/empleado/tipo-pago";
  const d = await fetchData(url);
  console.log("[Empleado] tipo-pago:", d);
  if (!d) return;
  if (!_datosOk(d)) { _mostrarVacio("chart-horas", "Sin datos de pagos"); return; }
  _limpiarVacio("chart-horas");
  const canvas = document.getElementById("chart-horas");
  if (!canvas) return;
  const ex = Chart.getChart(canvas); if (ex) ex.destroy();
  const COLORES = [
    "rgba(42,48,86,.85)", "rgba(67,176,175,.80)", "rgba(226,91,56,.80)",
    "rgba(103,255,242,.70)", "rgba(129,236,134,.75)",
  ];
  const BORDERS = ["#2A3056","#43B0AF","#E25B38","#67FFF2","#81EC86"];
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
      cutout: "60%",
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
              return `  ${c.parsed} pedido(s) · ${pct}%`;
            }
          }
        }
      }
    }
  });
}

/* ── Ingresos por método de entrega ───────────────── */
async function cargarIngresosMetodo() {
  const url = EMP_ID
    ? `/dashboard/api/empleado/ingresos-metodo?id=${EMP_ID}`
    : "/dashboard/api/empleado/ingresos-metodo";
  const d = await fetchData(url);
  console.log("[Empleado] ingresos-metodo:", d);
  if (!d) return;
  if (!_datosOk(d)) { _mostrarVacio("chart-ingresos-metodo", "Sin datos de ingresos"); return; }
  _limpiarVacio("chart-ingresos-metodo");
  const canvas = document.getElementById("chart-ingresos-metodo");
  if (!canvas) return;
  const ex = Chart.getChart(canvas); if (ex) ex.destroy();
  const COLORES = [
    "rgba(67,176,175,.85)","rgba(226,91,56,.80)","rgba(42,48,86,.80)",
    "rgba(103,255,242,.75)","rgba(129,236,134,.75)"];
  new Chart(canvas, {
    type: "bar",
    data: {
      labels: d.labels,
      datasets: [{
        label: "Ingresos (Bs)",
        data: d.data,
        backgroundColor: COLORES.slice(0, d.labels.length),
        borderRadius: 8,
        borderSkipped: false,
        barThickness: 30,
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 800, easing: "easeOutQuart" },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(30,35,64,.95)", cornerRadius: 10,
          callbacks: {
            label: (c) => `  Bs ${Number(c.parsed.x).toLocaleString("es-BO", { minimumFractionDigits: 2 })}`
          }
        }
      },
      scales: {
        x: { grid: { color: "rgba(67,176,175,.08)" }, ticks: { color: "#64748b", font: { size: 10 } },
             border: { display: false } },
        y: { grid: { display: false }, ticks: { color: "#2A3056", font: { size: 12, weight: "500" } },
             border: { display: false } }
      }
    }
  });
}

/* ── Cargar todo ──────────────────────────────────── */
document.addEventListener("DOMContentLoaded", function () {
  cargarKPIs();
  cargarEstado();
  cargarProductos();
  cargarHoras();
  cargarIngresosMetodo();
  cargarPedidos();
});