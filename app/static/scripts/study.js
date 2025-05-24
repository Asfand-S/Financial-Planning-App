function renderPieChart(ctxId, labels, data, colors) {
    const ctx = document.getElementById(ctxId).getContext('2d');

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    align: 'start',
                    labels: {
                        boxWidth: 24,
                        padding: 10,
                        font: {
                            size: 16
                        }
                    }
                }
            }
        }
    });
}
