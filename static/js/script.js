const submitButton = document.querySelector('button[type="submit"]');

submitButton.addEventListener('click', () => {
  submitButton.classList.add('loading');
  submitButton.disabled = true;
  submitButton.textContent = ' Загрузка...';
  spinner = document.createElement('i');
  spinner.classList.add('fa', 'fa-spinner', 'fa-spin');
  submitButton.insertBefore(spinner, submitButton.firstChild);
});