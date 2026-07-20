/*
 * SPDX-License-Identifier: Apache-2.0
 */

const palette = {
  passed: '#1fa2ff',
  failed: '#c1ddf1',
  skipped: '#e0e0e0',
  font: '#000000'
};
Chart.defaults.global.defaultFontColor = palette.font;

window.parseScoreboardUtcDate = function (value) {
  if (!value) {
    return null;
  }

  const match = value.match(
    /^(\d{2})\/(\d{2})\/(\d{4}) (\d{2}):(\d{2}):(\d{2})$/
  );
  if (!match) {
    return null;
  }

  const [, month, day, year, hour, minute, second] = match;
  return new Date(Date.UTC(
    Number(year),
    Number(month) - 1,
    Number(day),
    Number(hour),
    Number(minute),
    Number(second)
  ));
};

window.formatScoreboardDate = function (value, includeTime) {
  const date = window.parseScoreboardUtcDate(value);
  if (!date) {
    return value;
  }

  const formatOptions = includeTime
    ? {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }
    : {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      };

  return new Intl.DateTimeFormat(undefined, formatOptions).format(date);
};

window.formatScoreboardDateParts = function (value) {
  const date = window.parseScoreboardUtcDate(value);
  if (!date) {
    return null;
  }

  return {
    date: new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).format(date),
    time: new Intl.DateTimeFormat(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date)
  };
};

document.addEventListener('DOMContentLoaded', function () {
  const dateNodes = document.querySelectorAll('[data-utc-datetime]');

  dateNodes.forEach(node => {
    const utcValue = node.getAttribute('data-utc-datetime');
    const formatted = window.formatScoreboardDateParts(utcValue);

    if (formatted) {
      node.textContent = '';

      const dateSpan = document.createElement('span');
      dateSpan.textContent = formatted.date;

      const timeSpan = document.createElement('span');
      timeSpan.textContent = formatted.time;

      node.appendChild(dateSpan);
      node.appendChild(document.createElement('br'));
      node.appendChild(timeSpan);
    } else {
      node.textContent = window.formatScoreboardDate(utcValue, true);
    }

    node.setAttribute('title', utcValue + ' UTC');
  });
});
