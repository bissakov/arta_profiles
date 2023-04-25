function waitForElm(selector) {
  return new Promise(resolve => {
    if (document.querySelector(selector)) {
      return resolve(document.querySelector(selector));
    }

    const observer = new MutationObserver(mutations => {
      if (document.querySelector(selector)) {
        resolve(document.querySelector(selector));
        observer.disconnect();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  });
}

waitForElm('.family-portrait').then((element) => {
  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.classList.remove('loading');
  submitButton.disabled = false;
  submitButton.textContent = 'Запросить';
});

const fullNames = document.querySelectorAll('.fullName');
fullNames.forEach((fullNameEl) => {
  const words = fullNameEl.textContent.toLowerCase().split(' ');
  const modifiedWords = words.map((word) => word.charAt(0).toUpperCase() + word.slice(1));
  const modifiedString = modifiedWords.join(' ');
  fullNameEl.textContent = modifiedString;
});


const nums = document.querySelectorAll('.num');
nums.forEach((num) => {
  const textContent = num.textContent;
  if (/[a-zA-Zа-яА-Я]/.test(textContent)){
    return;
  }
  const value = parseFloat(textContent);
  const formattedValue = value.toLocaleString('en-US', { maximumFractionDigits: 2 });
  num.textContent = formattedValue.replace(',', ' ');
});