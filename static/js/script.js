const submitButton = document.querySelector('button[type="submit"]');

submitButton.addEventListener('click', () => {
  document.querySelector('form').submit()
  submitButton.classList.add('loading');
  submitButton.disabled = true;
  submitButton.textContent = ' Ожидание...';
  spinner = document.createElement('i');
  spinner.classList.add('fa', 'fa-spinner', 'fa-spin');
  submitButton.insertBefore(spinner, submitButton.firstChild);
});
