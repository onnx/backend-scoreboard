/*
 * SPDX-License-Identifier: Apache-2.0
 */

// Generate trend line chart
(function () {
  const content = document.getElementById('content');
  const lineTrend = document.getElementById('line_trend');
  const backendData = JSON.parse(content.getAttribute('backend_data'));
  const trendData = backendData.trend;
  const displayDataCount = 15;

  // Prepare list of label lists with date and package versions
  // Labels can be passed to the chart as a list of strings
  // or as a list of smaller lists with few labels (strings) for each element
  const labels = trendData.map( // For each summary in the trend
    summary => summary.versions ? [ // If summary has versions attribute (array)
      summary.date.split(' ')[0] // Create list with summary date (without time)
    ].concat(
      summary.versions.map( // Concat list of formatted package names and versions to the list with date
        corePackage => '\n' + corePackage.name + ': ' + corePackage.version.toString()
      )
    ) : summary.date.split(' ')[0] // Otherwise add only date (without time) as a label
  );

  function percentage (summary) {
    const total = summary.passed + summary.failed + summary.skipped;
    if (total === 0) {
      return 0.0;
    } else {
      return summary.passed / total * 100;
    }
  }

  const data = trendData.map(
    summary => percentage(summary).toFixed(2)
  );

  const lineChartData = {
    labels: [
      ['', '']
    ].concat(labels.slice(-displayDataCount)).concat(['']),
    datasets: [{
      data: ['None'].concat(data.slice(-displayDataCount)),
      label: 'Passed',
      fill: true,
      backgroundColor: 'transparent',
      borderColor: palette.passed,
      borderWidth: 2,
      pointBackgroundColor: palette.passed
    }]
  };

  new Chart(lineTrend, {
    type: 'line',
    data: lineChartData,
    options: {
      responsive: false,
      title: {
        fontSize: 25,
        display: true,
        text: 'Passed unit tests trend'
      },
      legend: {
        display: false,
        position: 'bottom'
      },
      scales: {
        xAxes: [{}],
        yAxes: [{
          ticks: {
            beginAtZero: true,
            suggestedMin: 0,
            suggestedMax: 100
          },
          scaleLabel: {
            fontSize: 20,
            display: true,
            labelString: 'unit tests %'
          }
        }]
      },
      elements: {
        line: {
          tension: 0 // Disable bezier curves
        }
      }
    }
  });
})();
