// Details trend chart
const lineTrend = document.getElementById('line_trend')
const frameworkData = JSON.parse(lineTrend.getAttribute('framework_data'))
const trendData = frameworkData.trend

const labels = trendData.map(
  summary => summary.versions ? [
    summary.date.split(' ')[0]
  ].concat(
    summary.versions.map(
      corePackage => '\n' + corePackage.name + ': ' + corePackage.version.toString()
    )
  ) : summary.date.split(' ')[0]
)

function percentage(summary) {
  let total = summary.passed + summary.failed + summary.skipped;
    if (total === 0) {
      return 0.0
    }
    else {
      return summary.passed / total * 100
    }
}

const data = trendData.map(
  summary => percentage(summary).toFixed(2)
)

const displayDataCount = 15
const lineChartData = {
  labels: [
    ['', '']
  ].concat(labels.slice(-displayDataCount)).concat(['']),
  datasets: [{
    data: [0].concat(data.slice(-displayDataCount)),
    label: 'Passed',
    fill: true,
    backgroundColor: 'transparent',
    borderColor: palette.passed,
    borderWidth: 2,
    pointBackgroundColor: palette.passed
  }]
}

new Chart(lineTrend, {
  type: 'line',
  data: lineChartData,
  options: {
    responsive: true,
    title: {
      fontSize: 20,
      display: false,
      text: 'Passed Unit Tests Trend'
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
        tension: 0 // Disables bezier curves
      }
    }
  }
})
