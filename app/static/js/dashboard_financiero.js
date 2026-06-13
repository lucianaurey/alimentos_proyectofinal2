/* ═══════════════════════════════════════════════════
   Foodly · dashboard_financiero.js
   KPIs de ingresos · Evolución · Por restaurante
═══════════════════════════════════════════════════ */

/* ── KPIs ─────────────────────────────────────────── */
async function cargarKPIs() {
  const data = await fetchData("/dashboard/api/financiero/kpis");
  if (data) renderKpis("kpis-container", data);
}

/* ── Evolución mensual ────────────────────────────── */
async function cargarEvolucion() {
  const d = await fetchData("/dashboard/api/financiero/evolucion");
  if (!d) return;
  crearGrafico("chart-evolucion", "line", d.labels, d.data, {
    money: true,
    label: "Ingresos Bs",
  });
}

/* ── Ingresos por restaurante (barra horizontal) ──── */
async function cargarRestaurantes() {
  const d = await fetchData("/dashboard/api/financiero/por-restaurante");
  if (!d) return;

  const canvas = document.getElementById("chart-restaurantes");
  if (!canvas) return;
  const ex = Chart.getChart(canvas);
  if (ex) ex.destroy();

  const barColors = (d.data || []).map((_, i) =>
    `rgba(67,176,175,${Math.max(1 - i * 0.07, 0.35)})`
  );

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
      }],
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
          bodyFont:  { size: 12, family: "'DM Sans'" },
          padding: { x: 14, y: 10 },
          cornerRadius: 10,
          callbacks: {
            label: (c) =>
              ` Bs ${Number(c.parsed.x).toLocaleString("es-BO", {
                minimumFractionDigits: 2,
              })}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(211,209,199,.15)" },
          ticks: {
            color: "#888780",
            callback: (v) => `Bs ${Number(v).toLocaleString("es-BO")}`,
          },
          border: { display: false },
        },
        y: {
          grid: { display: false },
          ticks: { color: "#150B08", font: { size: 11, weight: "500" } },
          border: { display: false },
        },
      },
    },
  });
}

/* ── Pedidos por estado (doughnut) ───────────────── */
async function cargarEstados() {
  const d = await fetchData("/dashboard/api/admin/pedidos-estado");
  if (!d) return;
  crearGrafico("chart-estados", "doughnut", d.labels, d.data);
}

/* ── Cargar todo ──────────────────────────────────── */
function cargarTodo() {
  cargarKPIs();
  cargarEvolucion();
  cargarRestaurantes();
  cargarEstados();
}

document.addEventListener("DOMContentLoaded", cargarTodo);