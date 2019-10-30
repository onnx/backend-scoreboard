// Table search
function onSearch (inputId, tableId) {
    const input = document.getElementById(inputId)
    const filter = input.value.toLowerCase()
    const table = document.getElementById(tableId)
    const testNames = table.getElementsByClassName('testName')
    const allFrameworkResults = table.getElementsByClassName('frameworkResults')

    for (let i = 0; i < testNames.length; i++) {
      const testNameText = testNames[i].textContent || testNames[i].innerText
      for (let j = 0; j < allFrameworkResults.length; j++) {
        const frameworkResults = allFrameworkResults[j].getElementsByClassName('testResult')
        if (testNameText.toLowerCase().indexOf(filter) < 0) {
          testNames[i].style.display = 'none'
          frameworkResults[i].style.display = 'none'
        } else {
          testNames[i].style.display = ''
          frameworkResults[i].style.display = ''
        }
      }
    }
  }
