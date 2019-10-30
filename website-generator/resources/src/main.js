// Get scoreboard database
const content = document.getElementById('content')
const database = JSON.parse(content.getAttribute('database'))

const palette = {
  passed: '#adff2f',
  failed: '#e93d27',
  font: '#c7d4d3'
}
Chart.defaults.global.defaultFontColor = palette.font

// // Generate circle charts
// for (const framework in database) {
//   const circleChart = document.getElementById('circle_' + database[framework].name)
//   const trend = database[framework].trend
//   const lastIdx = trend.length - 1
//   const chartData = {
//     labels: ['Passed', 'Failed'],
//     datasets: [{
//       backgroundColor: [palette.passed, palette.failed],
//       borderWidth: 0,
//       data: [trend[lastIdx].passed,
//         trend[lastIdx].failed
//       ]
//     }]
//   }

//   new Chart(circleChart, {
//     type: 'doughnut',
//     data: chartData,
//     options: {
//       legend: { display: false, position: 'bottom' },
//       cutoutPercentage: 80,
//       title: {
//         display: false,
//         text: database[framework].name
//       }
//     }
//   })
// }

// // Generate bar chart
// const barChart = document.getElementById('bar_chart')
// const barChartLabels = []
// const barChartDatasets = [{
//   data: [],
//   backgroundColor: palette.passed,
//   label: 'Passed',
//   barPercentage: 0.5,
//   barThickness: 1,
//   maxBarThickness: 3,
//   minBarLength: 2,
// },
// {
//   data: [],
//   backgroundColor: palette.failed,
//   label: 'Failed'
// }
// ]
// for (const framework in database) {
//   const trend = database[framework].trend
//   const lastIdx = trend.length - 1
//   barChartLabels.push(database[framework].name)
//   barChartDatasets[0].data.push(trend[lastIdx].passed)
//   barChartDatasets[1].data.push(trend[lastIdx].failed)
// }

// new Chart(barChart, {
//   type: 'bar',
//   data: {
//     labels: barChartLabels,
//     datasets: barChartDatasets
//   },
//   options: {
//     responsive: false,
//     title: {
//       fontSize: 25,
//       display: true,
//       text: 'Unit tests results'
//     },
//     legend: {
//       display: true,
//       position: 'bottom'
//     },
//     scales: {
//       xAxes: [{
//         barPercentage: 0.2,
//         categoryPercentage: 0.5
//       }],
//       yAxes: [{
//         ticks: {
//           beginAtZero: true
//         },
//         scaleLabel: {
//           fontSize: 20,
//           display: true,
//           labelString: 'unit tests'
//         }
//       }]
//     }
//   }
// })

// // Table search
// function onSearch (inputId, tableId) {
//   const input = document.getElementById(inputId)
//   const filter = input.value.toLowerCase()
//   const table = document.getElementById(tableId)
//   const testNames = table.getElementsByClassName('testName')
//   const allFrameworkResults = table.getElementsByClassName('frameworkResults')

//   for (let i = 0; i < testNames.length; i++) {
//     const testNameText = testNames[i].textContent || testNames[i].innerText
//     for (let j = 0; j < allFrameworkResults.length; j++) {
//       const frameworkResults = allFrameworkResults[j].getElementsByClassName('testResult')
//       if (testNameText.toLowerCase().indexOf(filter) < 0) {
//         testNames[i].style.display = 'none'
//         frameworkResults[i].style.display = 'none'
//       } else {
//         testNames[i].style.display = ''
//         frameworkResults[i].style.display = ''
//       }
//     }
//   }
// }
