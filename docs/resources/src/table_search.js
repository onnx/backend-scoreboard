/*
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * Search tests/operators by name and result.
 *
 * @param {String} inputId The id of an input field which contains a search name 
 * @param {String} tableId The id of a table with tests/operators
 * @param {String} tableType The type of entries in the table. Either 'Tests' or 'Ops' 
 */
(function () {
  function onSearch(inputId, tableId, tableType) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const testNames = table.getElementsByClassName('testName');
    const allBackendsResults = table.getElementsByClassName('backendResults');
    const showPassed = document.getElementById('showPassed' + tableType).checked;
    const showFailed = document.getElementById('showFailed' + tableType).checked;
    let testStatus = '';

    if (showPassed && !showFailed) {
      testStatus = 'passed';
    }
    else if (showFailed && !showPassed) {
      testStatus = 'failed';
    }
    for (let i = 0; i < testNames.length; i++) {
      const testNameText = testNames[i].textContent || testNames[i].innerText;
      for (let j = 0; j < allBackendsResults.length; j++) {
        const backendResults = allBackendsResults[j].getElementsByClassName('testResult');
        const testResult = backendResults[i].textContent.trim().toLowerCase();
        if (testNameText.toLowerCase().indexOf(filter) < 0 || (testStatus && testResult !== testStatus)) {
          testNames[i].style.display = 'none';
          backendResults[i].style.display = 'none';
        } else {
          testNames[i].style.display = '';
          backendResults[i].style.display = '';
        }
      }
    }
  }
  window.onSearch = onSearch;
})();
