const nums = document.querySelectorAll('.num');

nums.forEach((num) => {
  const value = parseFloat(num.textContent);
  const formattedValue = value.toLocaleString('en-US', { maximumFractionDigits: 2 });
  num.textContent = formattedValue.replace(',', ' ');
});