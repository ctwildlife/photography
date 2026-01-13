document.addEventListener("DOMContentLoaded", () => {
  const nav = document.getElementById("navbar");
  if (!nav) return;

  nav.innerHTML = `
    <div style="
      background:red;
      color:white;
      padding:20px;
      font-size:24px;
      font-weight:bold;
    ">
      JS IS RUNNING AND INJECTING HTML
    </div>
  `;
});
