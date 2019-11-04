// Table search
(function () {
  function onSearch (inputId, tableId) {
    const input = document.getElementById(inputId)
    const filter = input.value.toLowerCase()
    const table = document.getElementById(tableId)
    const testNames = table.getElementsByClassName('testName')
    const allBackendsResults = table.getElementsByClassName('backendResults')

    for (let i = 0; i < testNames.length; i++) {
      const testNameText = testNames[i].textContent || testNames[i].innerText
      for (let j = 0; j < allBackendsResults.length; j++) {
        const backendResults = allBackendsResults[j].getElementsByClassName('testResult')
        if (testNameText.toLowerCase().indexOf(filter) < 0) {
          testNames[i].style.display = 'none'
          backendResults[i].style.display = 'none'
        } else {
          testNames[i].style.display = ''
          backendResults[i].style.display = ''
        }
      }
    }
  }
  window.onSearch = onSearch
})()
