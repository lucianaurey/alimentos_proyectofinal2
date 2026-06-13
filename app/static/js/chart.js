/* ═══════════════════════════════════════════════════
   Foodly · chart.js – Premium Charts v2
   Smooth gradients · Glowing effects · Rich tooltips
═══════════════════════════════════════════════════ */

// ── Paleta Foodly (colores oficiales del landing) ─────────────────
// #2A3056 (navy) · #43B0AF (brand teal) · #67FFF2 (cyan) · #81EC86 (green)
const FOODLY = {
  negro:      "#2A3056",
  rojoclaro:  "#43B0AF",
  rojo:       "#67FFF2",
  platino:    "#E9ECEF",
  crema:      "#f0f5f4",
  gris:       "#64748b",
  colores: [
    "#43B0AF","#2A3056","#67FFF2","#81EC86",
    "#446B5C","#294933","#3a9d9c","#1e2340",
    "#5bc8c7","#94a3b8"
  ],
  gradientes: {
    naranja: ["#43B0AF","#67FFF2"],
    rojo:    ["#67FFF2","#43B0AF"],
    negro:   ["#1e2340","#2A3056"],
    platino: ["#E9ECEF","#c5d5d3"],
    green:   ["#81EC86","#446B5C"],
  },
};

// ── Opciones por defecto ─────────────────────────────────────────
Chart.defaults.font.family   = "'DM Sans', sans-serif";
Chart.defaults.font.size     = 12;
Chart.defaults.color         = "#888780";
Chart.defaults.plugins.legend.position = "bottom";
Chart.defaults.plugins.legend.labels = {
  ...Chart.defaults.plugins.legend.labels,
  usePointStyle: true,
  pointStyle: "circle",
  padding: 16,
  font: { size: 11, family: "'DM Sans', sans-serif", weight: '500' },
};

// ── Helper: crear gradiente para canvas ──────────────────────────
function crearGradiente(ctx, colores, vertical = true) {
  const h = ctx.canvas.clientHeight || 300;
  const w = ctx.canvas.clientWidth || 500;
  const grad = vertical
    ? ctx.createLinearGradient(0, 0, 0, h)
    : ctx.createLinearGradient(0, 0, w, 0);
  grad.addColorStop(0, colores[0] + "DD");
  grad.addColorStop(1, colores[1] + "40");
  return grad;
}

function crearGradienteSolido(ctx, colores, vertical = true) {
  const h = ctx.canvas.clientHeight || 300;
  const w = ctx.canvas.clientWidth || 500;
  const grad = vertical
    ? ctx.createLinearGradient(0, 0, 0, h)
    : ctx.createLinearGradient(0, 0, w, 0);
  grad.addColorStop(0, colores[0]);
  grad.addColorStop(1, colores[1]);
  return grad;
}

// ── Helper: fetch JSON desde una API ────────────────────────────
async function fetchData(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn("Foodly charts — error fetching", url, e);
    return null;
  }
}

// ── Crear gráfico genérico con gradientes ────────────────────────
function crearGrafico(canvasId, tipo, labels, data, opciones = {}) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  // Destruir instancia previa si existe
  const existing = Chart.getChart(canvas);
  if (existing) existing.destroy();

  const ctx = canvas.getContext("2d");

  // Si no hay datos, mostrar mensaje amigable
  if (!labels || !data || labels.length === 0 || data.length === 0 || data.every(v => v === 0 || v === null || v === undefined)) {
    // Limpiar canvas y mostrar mensaje
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const parent = canvas.parentElement;
    if (parent) {
      // Crear overlay de "sin datos"
      let emptyMsg = parent.querySelector('.chart-empty-msg');
      if (!emptyMsg) {
        emptyMsg = document.createElement('div');
        emptyMsg.className = 'chart-empty-msg';
        emptyMsg.innerHTML = `
          <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;min-height:200px;gap:12px;">
            <i class="fa-solid fa-chart-simple" style="font-size:40px;background:linear-gradient(135deg,#43B0AF,#67FFF2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;opacity:.5;"></i>
            <span style="font-size:13px;color:#94a3b8;font-weight:500;font-family:'Outfit',sans-serif;">Sin datos disponibles</span>
            <span style="font-size:11px;color:#64748b;font-family:'Inter',sans-serif;">Los datos aparecerán aquí cuando estén disponibles</span>
          </div>
        `;
        parent.appendChild(emptyMsg);
      }
      canvas.style.display = 'none';
    }
    return null;
  }

  // Asegurar que canvas es visible
  canvas.style.display = '';
  const emptyMsg = canvas.parentElement?.querySelector('.chart-empty-msg');
  if (emptyMsg) emptyMsg.remove();

  // Colores según tipo
  let backgroundColor, borderColor, borderWidth = 0;

  if (tipo === "doughnut" || tipo === "pie") {
    backgroundColor = FOODLY.colores.map(c => c + "DD");
    borderColor = "#fff";
    borderWidth = 3;
  } else if (tipo === "line") {
    const grad = crearGradiente(ctx, FOODLY.gradientes.naranja);
    backgroundColor = grad;
    borderColor = FOODLY.rojoclaro;
    borderWidth = 2.5;
  } else {
    // Bar charts con gradiente
    const grad = crearGradienteSolido(ctx, FOODLY.gradientes.naranja);
    backgroundColor = grad;
    borderColor = "transparent";
    borderWidth = 0;
  }

  const config = {
    type: tipo,
    data: {
      labels,
      datasets: [{
        label:           opciones.label || "",
        data,
        backgroundColor,
        borderColor,
        borderWidth,
        tension:         0.4,
        fill:            tipo === "line",
        pointRadius:     tipo === "line" ? 4 : 0,
        pointBackgroundColor: tipo === "line" ? "#fff" : undefined,
        pointBorderColor: tipo === "line" ? FOODLY.rojoclaro : undefined,
        pointBorderWidth: tipo === "line" ? 2.5 : undefined,
        pointHoverRadius: tipo === "line" ? 7 : undefined,
        pointHoverBackgroundColor: tipo === "line" ? FOODLY.rojoclaro : undefined,
        pointHoverBorderColor: tipo === "line" ? "#fff" : undefined,
        pointHoverBorderWidth: tipo === "line" ? 3 : undefined,
        borderRadius:    tipo === "bar" ? 8 : 0,
        borderSkipped:   false,
        hoverBackgroundColor: tipo === "doughnut" || tipo === "pie"
          ? FOODLY.colores.map(c => c + "FF")
          : undefined,
      }],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      animation: {
        duration: 800,
        easing: "easeOutQuart",
      },
      interaction: {
        intersect: false,
        mode: tipo === "doughnut" || tipo === "pie" ? "nearest" : "index",
      },
      plugins: {
        legend: {
          display: tipo === "doughnut" || tipo === "pie",
        },
        tooltip: {
          backgroundColor: "rgba(30,35,64,.95)",
          titleFont: { size: 13, weight: "600", family: "'DM Sans'" },
          bodyFont:  { size: 12, family: "'DM Sans'" },
          padding: { x: 14, y: 10 },
          cornerRadius: 10,
          displayColors: tipo === "doughnut" || tipo === "pie",
          boxPadding: 6,
          caretSize: 6,
          callbacks: {
            label: function (ctx) {
              const v = ctx.parsed.y ?? ctx.parsed;
              if (opciones.money) {
                return ` Bs ${Number(v).toLocaleString("es-BO", { minimumFractionDigits: 2 })}`;
              }
              return ` ${Number(v).toLocaleString("es-BO")}`;
            },
          },
        },
      },
      scales: (tipo === "doughnut" || tipo === "pie") ? {} : {
        x: {
          grid: {
            display: false,
          },
          ticks: {
            font: { size: 11, weight: "500" },
            color: "#888780",
            maxRotation: 45,
          },
          border: { display: false },
        },
        y: {
          grid: {
            color: "rgba(211,209,199,.2)",
            drawBorder: false,
          },
          ticks: {
            font: { size: 11, weight: "500" },
            color: "#888780",
            padding: 8,
            callback: (v) => opciones.money
              ? `Bs ${Number(v).toLocaleString("es-BO")}`
              : Number(v).toLocaleString("es-BO"),
          },
          border: { display: false },
        },
      },
      ...opciones.chartOptions,
    },
  };

  // Special doughnut styling
  if (tipo === "doughnut") {
    config.options.cutout = "72%";
    config.options.plugins.legend = {
      display: true,
      position: "bottom",
      labels: {
        usePointStyle: true,
        pointStyle: "circle",
        padding: 14,
        font: { size: 11, family: "'DM Sans'", weight: "500" },
      },
    };
  }

  return new Chart(canvas, config);
}

// ── Cargar KPIs en tarjetas ──────────────────────────────────────
function renderKpis(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container || !Array.isArray(data)) return;

  const toneClass = { negro: "", orange: "icon-orange", red: "icon-red", teal: "icon-teal" };

  container.innerHTML = data.map((k, i) => `
    <div class="col" style="animation-delay:${0.05 + i * 0.06}s">
      <div class="kpi-card">
        <div class="kpi-icon ${toneClass[k.tone] || ''}">
          <i class="fa-solid ${k.icon}"></i>
        </div>
        <div class="kpi-body">
          <div class="kpi-value">${k.value}</div>
          <div class="kpi-label">${k.title}</div>
        </div>
      </div>
    </div>
  `).join("");
}

// ── Cargar tabla dinámica ────────────────────────────────────────
function renderTabla(tbodyId, theadId, data) {
  const tbodyEl = document.getElementById(tbodyId);
  const theadEl = document.getElementById(theadId);
  if (!theadEl || !tbodyEl || !data) return;

  // Find the parent <table> element from the tbody
  const tableEl = tbodyEl.closest("table");
  if (!tableEl) return;
  const tableId = tableEl.id;

  // Destruir instancia previa si existe
  if (window.jQuery && $.fn.DataTable && tableId && $.fn.DataTable.isDataTable(`#${tableId}`)) {
    $(`#${tableId}`).DataTable().destroy();
  }

  // Limpiar thead y tbody
  theadEl.innerHTML = "";
  tbodyEl.innerHTML = "";

  if (!data.columns || !data.rows) return;

  const keys = data.rows.length > 0 ? Object.keys(data.rows[0]) : [];

  // Construir columnas para DataTables (mapeo key → columna)
  const dtColumns = data.columns.map((title, i) => ({
    title: title,
    data:  keys[i] ?? null,
    defaultContent: "—",
    render: (val) => (val === null || val === undefined) ? "—" : val,
  }));

  // Inicializar DataTables pasándole la data directamente (sin leer HTML)
  if (window.jQuery && $.fn.DataTable && tableId) {
    setTimeout(() => {
      $(`#${tableId}`).DataTable({
        data:     data.rows,
        columns:  dtColumns,
        language: { url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json" },
        pageLength: 10,
        responsive: true,
        dom: '<"dt-top"lf>rt<"dt-bottom"ip>',
        destroy: true,
      });
    }, 0);
  }
}

// ── Init DataTable (legacy, para tablas con HTML estático) ───────
function initDataTable(tableId) {
  const el = document.getElementById(tableId);
  if (!el || !window.jQuery || !$.fn.DataTable) return;
  if ($.fn.DataTable.isDataTable(`#${tableId}`)) return;

  $(`#${tableId}`).DataTable({
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
    },
    pageLength: 10,
    responsive: true,
    dom: '<"dt-top"lf>rt<"dt-bottom"ip>',
  });
}