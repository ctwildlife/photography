document.addEventListener("DOMContentLoaded", function () {
    fetch("/photography/pages/nav.html")  // path to your nav HTML
        .then(response => response.text())
        .then(data => {
            document.getElementById("navbar").innerHTML = data;
        })
        .catch(error => console.error("Error loading nav:", error));
});
