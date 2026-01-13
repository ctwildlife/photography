// load-nav.js

window.addEventListener("DOMContentLoaded", () => {
  console.log("load-nav.js running"); // confirms script executes

  const navbar = document.getElementById("navbar");
  if (!navbar) {
    console.error("No element with id 'navbar' found.");
    return;
  }

  // TEMP TEST: show obvious injected menu
  navbar.innerHTML = "<p style='color:red; font-weight:bold;'>[Injected menu placeholder]</p>";

  // Real fetch of nav.html
  fetch("/photography/includes/nav.html")
    .then(response => {
      console.log("Nav fetch response status:", response.status);
      if (!response.ok) throw new Error("Nav fetch failed with status " + response.status);
      return response.text();
    })
    .then(html => {
      console.log("HTML fetched from nav.html:", html); // shows exactly what was fetched
      navbar.innerHTML += html; // append below the red placeholder
    })
    .catch(err => {
      console.error("Failed to load nav:", err);
      navbar.innerHTML += "<p>Menu failed to load.</p>"; // fallback in page
    });
});
