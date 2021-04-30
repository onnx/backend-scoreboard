/*
 * SPDX-License-Identifier: Apache-2.0
 */

// Generate circle charts
(function () {
  const content = document.getElementById('content');
  const database = JSON.parse(content.getAttribute('database'));

  for (const backend in database) {
    const circleChart = document.getElementById('circle_' + database[backend].name);
    const trend = database[backend].trend;
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
    };

    new Chart(circleChart, {
      type: 'doughnut',
      data: chartData,
      options: {
        legend: { display: false, position: 'bottom' },
        cutoutPercentage: 80,
        title: {
          display: false,
          text: database[backend].name
        }
      }
    });
  }
})();
