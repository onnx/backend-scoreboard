/*
 * SPDX-License-Identifier: Apache-2.0
 */

// Generate bar chart
(function () {
  const content = document.getElementById('content');
  const backendData = JSON.parse(content.getAttribute('backend_data'));

  const barChart = document.getElementById('bar_chart');
  const barChartLabels = [];
  const barChartDatasets = [{
    data: [],
    backgroundColor: palette.passed,
    label: 'Passed'
  },
  {
    data: [],
    backgroundColor: palette.failed,
    label: 'Failed'
  }];

  const trend = backendData.trend;
  const lastIdx = trend.length - 1;
  barChartLabels.push(backendData.name);
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
          barPercentage: 0.65,  // Bars width
          categoryPercentage: 0.5  // Bars space
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
  });
})();
