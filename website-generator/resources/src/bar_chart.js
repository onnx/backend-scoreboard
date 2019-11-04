// Generate bar chart
(function () {
  const content = document.getElementById('content')
  const framework_data = JSON.parse(content.getAttribute('framework_data'))

  const barChart = document.getElementById('bar_chart')
  const barChartLabels = []
  const barChartDatasets = [{
    data: [],
    backgroundColor: palette.passed,
    label: 'Passed',
    barPercentage: 0.5,
    barThickness: 1,
    maxBarThickness: 3,
    minBarLength: 2,
  },
  {
    data: [],
    backgroundColor: palette.failed,
    label: 'Failed'
  }];

  const trend = framework_data.trend;
  const lastIdx = trend.length - 1;
  barChartLabels.push(framework_data.name);
  barChartDatasets[0].data.push(trend[lastIdx].passed);
  barChartDatasets[1].data.push(trend[lastIdx].failed);

  new Chart(barChart, {
    type: 'bar',
    data: {
      labels: barChartLabels,
      datasets: barChartDatasets
    },
    options: {
      responsive: false,
      title: {
        fontSize: 25,
        display: true,
        text: 'Unit tests results'
      },
      legend: {
        display: true,
        position: 'bottom'
      },
      scales: {
        xAxes: [{
          barPercentage: 0.2,
          categoryPercentage: 0.5
        }],
        yAxes: [{
          ticks: {
            beginAtZero: true
          },
          scaleLabel: {
            fontSize: 20,
            display: true,
            labelString: 'unit tests'
          }
        }]
      }
    }
  })
})()
