// load-nav.js
fetch("/photography/includes/nav.html")
  .then(response => response.text())
  .then(html => {
    document.getElementById("navbar").innerHTML = html;
  })
  .catch(err => console.error("Failed to load nav:", err));
