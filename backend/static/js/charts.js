document.addEventListener("DOMContentLoaded", function() {
    const chartDiv = document.getElementById('chartData');

    const labels = JSON.parse(chartDiv.dataset.labels);
    const soilBenefits = JSON.parse(chartDiv.dataset.soil);

    const ctx = document.getElementById('cropChart').getContext('2d');

    if (labels.length === 0 || soilBenefits.length === 0) {
        ctx.font = "16px Arial";
        ctx.fillStyle = "gray";
        ctx.textAlign = "center";
        ctx.fillText("No data yet", ctx.canvas.width / 2, ctx.canvas.height / 2);
        return;
    }

    
    function getRandomColor() {
        const r = Math.floor(Math.random() * 255);
        const g = Math.floor(Math.random() * 255);
        const b = Math.floor(Math.random() * 255);
        return `rgba(${r}, ${g}, ${b}, 0.7)`;
    }

    const colorMap = {
        "wheat": 'rgba(255, 99, 132, 0.7)',
        "maize": 'rgba(54, 162, 235, 0.7)',
        "rice": 'rgba(255, 206, 86, 0.7)',
        "sugarcane": 'rgba(75, 192, 192, 0.7)',
        "pulses": 'rgba(153, 102, 255, 0.7)',
        "oats": 'rgba(255, 159, 64, 0.7)'
    };

    const backgroundColors = labels.map(label => {
        let cleanLabel = label.replace(/[^a-zA-Z]/g, '').toLowerCase();
        console.log("Original:", label, "| Clean:", cleanLabel);

        return colorMap[cleanLabel] || getRandomColor();
    });

    const borderColors = backgroundColors.map(c => c.replace('0.7', '1'));

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Soil Benefit Score',
                data: soilBenefits,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});