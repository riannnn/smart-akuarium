document.addEventListener("DOMContentLoaded", () => {
  const modalOverlay = document.getElementById("modalOverlay");
  const tabLogin = document.getElementById("tabLogin");
  const tabRegister = document.getElementById("tabRegister");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("register_user");

  document.getElementById("openLoginBtn")?.addEventListener("click", () => {
    modalOverlay.style.display = "flex";
    tabLogin?.click();
  });

  document.getElementById("openRegisterBtn")?.addEventListener("click", () => {
    modalOverlay.style.display = "flex";
    tabRegister?.click();
  });

  document.getElementById("closeModalBtn")?.addEventListener("click", () => {
    modalOverlay.style.display = "none";
  });

  tabLogin?.addEventListener("click", () => {
    loginForm.style.display = "flex";
    registerForm.style.display = "none";
    tabLogin.classList.add("active");
    tabRegister?.classList.remove("active");
  });

  tabRegister?.addEventListener("click", () => {
    loginForm.style.display = "none";
    registerForm.style.display = "flex";
    tabRegister.classList.add("active");
    tabLogin?.classList.remove("active");
  });

  modalOverlay?.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.style.display = "none";
    }
  });

  // Lindungi link jika user belum login
  if (window.isLoggedIn === false || window.isLoggedIn === "false") {
    document.querySelectorAll("[data-protected]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        alert("Silakan login atau register terlebih dahulu!");
        modalOverlay.style.display = "flex";
        tabLogin?.click();
      });
    });
  }
});
