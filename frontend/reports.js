// reports.js
document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'https://cafe-system-7nhg.onrender.com';

    // Elementos del DOM
    const totalRevenueEl = document.getElementById('total-revenue');
    const totalSalesEl = document.getElementById('total-sales');
    const averageTicketEl = document.getElementById('average-ticket');
    const filterButtons = document.querySelectorAll('.filters .btn[data-range]');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const customRangeBtn = document.getElementById('custom-range-btn');

    let topProductsChart;

    // Función para formatear fechas a YYYY-MM-DD
    const formatDate = (date) => date.toISOString().split('T')[0];

    // Función principal para cargar datos y actualizar la UI
    const fetchReportData = async (startDate, endDate) => {
        try {
            const response = await fetch(`${API_URL}/reports/summary?start_date=${startDate}&end_date=${endDate}`);
            const data = await response.json();

            totalRevenueEl.textContent = `$ ${data.total_revenue.toLocaleString('es-AR', { minimumFractionDigits: 2 })}`;
            totalSalesEl.textContent = data.total_sales;
            averageTicketEl.textContent = `$ ${data.average_ticket.toLocaleString('es-AR', { minimumFractionDigits: 2 })}`;

            updateChart(data.top_products);
        } catch (error) {
            console.error("Error al cargar reportes:", error);
        }
    };

    // Función para actualizar el gráfico
    const updateChart = (topProducts) => {
        const ctx = document.getElementById('top-products-chart').getContext('2d');
        
        if (topProductsChart) {
            topProductsChart.destroy();
        }

        topProductsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topProducts.map(p => p.name),
                datasets: [{
                    label: 'Cantidad Vendida',
                    data: topProducts.map(p => p.quantity),
                    backgroundColor: '#6D4C41',
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y', // Barras horizontales
                scales: { x: { beginAtZero: true } }
            }
        });
    };
    
    // Lógica de los filtros de fecha
    const handleFilterClick = (e) => {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');

        const range = e.target.dataset.range;
        const today = new Date();
        let startDate, endDate = formatDate(today);

        if (range === 'today') {
            startDate = formatDate(today);
        } else if (range === 'week') {
            const dayOfWeek = today.getDay();
            const firstDayOfWeek = new Date(today.setDate(today.getDate() - dayOfWeek));
            startDate = formatDate(firstDayOfWeek);
        } else if (range === 'month') {
            startDate = formatDate(new Date(today.getFullYear(), today.getMonth(), 1));
        }
        
        startDateInput.value = startDate;
        endDateInput.value = endDate;
        fetchReportData(startDate, endDate);
    };

    filterButtons.forEach(button => button.addEventListener('click', handleFilterClick));
    customRangeBtn.addEventListener('click', () => {
        const start = startDateInput.value;
        const end = endDateInput.value;
        if (start && end) {
            fetchReportData(start, end);
        }
    });

    // Carga inicial (reporte del día de hoy)
    document.querySelector('.filters .btn[data-range="today"]').click();
});