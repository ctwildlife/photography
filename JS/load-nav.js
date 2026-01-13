window.addEventListener("DOMContentLoaded", () => {
  const navbar = document.getElementById("navbar");
  if (!navbar) {
    console.error("No element with id 'navbar' found.");
    return;
  }

  fetch("/photography/includes/nav.html")
    .then(response => {
      if (!response.ok) throw new Error("Nav fetch failed: " + response.status);
      return response.text();
    })
    .then(html => {
      navbar.innerHTML = html;
    })
    .catch(err => {
      console.error("Failed to load nav:", err);
      navbar.innerHTML = "<p>Menu failed to load.</p>";
    });
});
