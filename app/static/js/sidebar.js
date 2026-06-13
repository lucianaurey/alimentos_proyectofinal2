/* Foodly · sidebar.js */
document.addEventListener("DOMContentLoaded", function () {
  const sidebar    = document.getElementById("sidebar");
  const mainWrapper = document.getElementById("mainWrapper");
  const toggleBtn  = document.getElementById("sidebarToggle");

  if (!sidebar || !toggleBtn) return;

  toggleBtn.addEventListener("click", function () {
    sidebar.classList.toggle("collapsed");
    mainWrapper && mainWrapper.classList.toggle("sidebar-collapsed");
    localStorage.setItem("sidebarCollapsed", sidebar.classList.contains("collapsed"));
  });

  // Restaurar estado guardado
  if (localStorage.getItem("sidebarCollapsed") === "true") {
    sidebar.classList.add("collapsed");
    mainWrapper && mainWrapper.classList.add("sidebar-collapsed");
  }
});