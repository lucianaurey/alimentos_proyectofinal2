/* ═══════════════════════════════════════════════════
   Foodly · dashboard_admin.js – Premium v3
   Rich gradients · Custom horizontal bars · Smart fallbacks
═══════════════════════════════════════════════════ */

function filtros() {
  const anio = document.getElementById("f-anio")?.value || "";
  const mes = document.getElementById("f-mes")?.value || "";
  const zona = document.getElementById("f-zona")?.value || "";
  return new URLSearchParams({ anio, mes, zona });
}

/* ── KPIs ─────────────────────────────────────────── */
async function cargarKPIs() {
  const data = await fetchData(`/dashboard/api/admin/kpis?${filtros()}`);
  if (data) renderKpis("kpis-container", data);
}

/* ── Ventas por mes ───────────────────────────────── */
async function cargarVentasMes() {
  const d = await fetchData(`/dashboard/api/admin/ventas-mes?${filtros()}`);
  if (!d) return;
  console.log("[Admin] ventas-mes:", d);
  crearGrafico("chart-ventas-mes", "line", d.labels, d.data, { money: true, label: "Ingresos Bs" });
}

/* ── Pedidos por estado ───────────────────────────── */
async function cargarEstado() {
  const d = await fetchData("/dashboard/api/admin/pedidos-estado");
  if (!d) return;
  console.log("[Admin] pedidos-estado:", d);
  crearGrafico("chart-pedidos-estado", "doughnut", d.labels, d.data);
}

/* ── Top restaurantes (barra horizontal premium) ──── */
async function cargarTop() {
  const d = await fetchData(`/dashboard/api/admin/top-restaurantes?${filtros()}`);
  if (!d) return;
  console.log("[Admin] top-restaurantes:", d);

  const canvas = document.getElementById("chart-top-restaurantes");
  if (!canvas) return;
  const existing = Chart.getChart(canvas);
  if (existing) existing.destroy();

  // Handle empty data
  if (!d.labels || !d.data || d.labels.length === 0 || d.data.length === 0) {
    crearGrafico("chart-top-restaurantes", "bar", [], []);
    return;
  }

  const ctx = canvas.getContext("2d");

  // Teal palette gradient for each bar
  const barColors = d.data.map((_, i) => {
    const alpha = 1 - (i * 0.07);
    return `rgba(67,176,175,${Math.max(alpha, 0.35)})`;
  });

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: d.labels,
      datasets: [{
        label: "Ingresos Bs",
        data: d.data,
        backgroundColor: barColors,
        borderRadius: 6,
        borderSkipped: false,
        barThickness: 22,
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
            label: (ctx) => ` Bs ${Number(ctx.parsed.x).toLocaleString("es-BO", { minimumFractionDigits: 2 })}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(211,209,199,.15)" },
          ticks: { font: { size: 10, weight: "500" }, color: "#888780",
            callback: (v) => `Bs ${Number(v).toLocaleString("es-BO")}`,
          },
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

/* ── Pedidos por zona ─────────────────────────────── */
async function cargarZona() {
  const d = await fetchData(`/dashboard/api/admin/pedidos-zona?${filtros()}`);
  if (!d) return;
  console.log("[Admin] pedidos-zona:", d);
  crearGrafico("chart-pedidos-zona", "bar", d.labels, d.data, { label: "Pedidos" });
}

/* ── Ranking (tabla) ──────────────────────────────── */
async function cargarRanking() {
  const data = await fetchData(`/dashboard/api/admin/ranking?${filtros()}`);
  if (!data) return;

  const rows = (data.rows || []).map((r, i) => ({
    "#":              `<span style="font-weight:700;color:${i < 3 ? 'var(--rojo-claro)' : 'var(--texto-ter)'};font-size:13px;">${i + 1}</span>`,
    "Restaurante":    `<span style="font-weight:600;">${r.nombre || "—"}</span>`,
    "Zona":           r.zona && r.zona !== "—"
                        ? `<span style="font-size:11px;background:linear-gradient(135deg,var(--platino),#d4d7db);color:var(--negro);padding:3px 10px;border-radius:12px;font-weight:500;">
                            <i class='fa-solid fa-location-dot' style='font-size:9px;'></i> ${r.zona}</span>`
                        : "—",
    "Pedidos":        r.total_pedidos || "0",
    "Ingresos":       `<span style="font-weight:600;color:var(--negro);">${r.ingresos || "Bs 0.00"}</span>`,
    "Ticket prom.":   r.ticket_promedio || "Bs 0.00",
  }));

  renderTabla("tbody-ranking", "thead-ranking", {
    columns: ["#", "Restaurante", "Zona", "Pedidos", "Ingresos", "Ticket prom."],
    rows,
  });
}

/* ── Cargar todo ──────────────────────────────────── */
function cargarTodo() {
  cargarKPIs();
  cargarVentasMes();
  cargarEstado();
  cargarTop();
  cargarZona();
  cargarRanking();
}

document.addEventListener("DOMContentLoaded", cargarTodo);