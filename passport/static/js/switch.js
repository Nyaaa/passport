var settings = localStorage.getItem('lightSwitch');

function getSystemDefaultTheme() {
  const darkThemeMq = window.matchMedia('(prefers-color-scheme: dark)');
  if (darkThemeMq.matches) {
    return 'dark';
  }
  return 'light';
}

if (settings == null) {
  settings = getSystemDefaultTheme();
  }

if (settings == 'dark') {
  document.documentElement.setAttribute('data-bs-theme','dark');
  document.getElementById('lightSwitch').innerHTML = '<i class="fa-regular fa-sun"></i>';
}

document.getElementById('lightSwitch').addEventListener('click',()=>{
  if (document.documentElement.getAttribute('data-bs-theme') == 'dark') {
    document.documentElement.setAttribute('data-bs-theme','light');
    localStorage.setItem('lightSwitch', 'light')
    document.getElementById('lightSwitch').innerHTML = '<i class="fa-regular fa-moon"></i>';
  } else {
    document.documentElement.setAttribute('data-bs-theme','dark');
    localStorage.setItem('lightSwitch', 'dark')
    document.getElementById('lightSwitch').innerHTML = '<i class="fa-regular fa-sun"></i>';
  }
})