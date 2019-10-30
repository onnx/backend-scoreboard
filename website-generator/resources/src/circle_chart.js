// Generate circle charts
(function () {
  const content = document.getElementById('content');
  const database = JSON.parse(content.getAttribute('database'));

  for (const framework in database) {
    const circleChart = document.getElementById('circle_' + database[framework].name);
    const trend = database[framework].trend;
    const lastIdx = trend.length - 1;
    const chartData = {
      labels: ['Passed', 'Failed'],
      datasets: [{
        backgroundColor: [palette.passed, palette.failed],
        borderWidth: 0,
        data: [trend[lastIdx].passed,
          trend[lastIdx].failed
        ]
      }]
    }

    new Chart(circleChart, {
      type: 'doughnut',
      data: chartData,
      options: {
        legend: { display: false, position: 'bottom' },
        cutoutPercentage: 80,
        title: {
          display: false,
          text: database[framework].name
        }
      }
    })
  }
})()
