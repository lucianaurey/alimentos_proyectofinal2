/* Foodly · tables.js */
document.addEventListener("DOMContentLoaded", function () {
  // Inicializa cualquier tabla con clase .foodly-table automáticamente
  document.querySelectorAll("table.foodly-table").forEach(function (table) {
    if (window.jQuery && $.fn.DataTable && !$.fn.DataTable.isDataTable(table)) {
      $(table).DataTable({
        language: {
          url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10,
        responsive: true,
      });
    }
  });
});