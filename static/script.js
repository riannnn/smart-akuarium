document.addEventListener("DOMContentLoaded", () => {
  // Utuk menjaalankan fungsi polling hanya kalau fungsi tersebut memang ada di halaman
  if (typeof fetchData === "function") {
    fetchData();
    setInterval(fetchData, 3000);
  }

  if (typeof fetchHistoryData === "function") {
    fetchHistoryData();
    setInterval(fetchHistoryData, 30000);
  }

  if (typeof checkAnomaly === "function") {
    checkAnomaly();
    setInterval(checkAnomaly, 10000);
  }

  // Berfungsi untuk cek apakah modal sudah ada di halaman ini apa belom
  const modalOverlay = document.getElementById("modalOverlay");
  if (!modalOverlay) {
    // jika gaada ada modal (misalnya di halaman monitoring), stop di sini
    return;
  }

  const tabLogin = document.getElementById("tabLogin");
  const tabRegister = document.getElementById("tabRegister");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("register_user");

  document.getElementById("openLoginBtn")?.addEventListener("click", () => {
    modalOverlay.style.display = "flex";
    tabLogin?.click();
    clearLoginForm();
  });

  document.getElementById("openRegisterBtn")?.addEventListener("click", () => {
    modalOverlay.style.display = "flex";
    tabRegister?.click();
    clearRegisterForm();
  });

  document.getElementById("closeModalBtn")?.addEventListener("click", () => {
    modalOverlay.style.display = "none";
  });

  tabLogin?.addEventListener("click", () => {
    if (loginForm) loginForm.style.display = "flex";
    if (registerForm) registerForm.style.display = "none";
    tabLogin.classList.add("active");
    tabRegister?.classList.remove("active");
  });

  tabRegister?.addEventListener("click", () => {
    if (loginForm) loginForm.style.display = "none";
    if (registerForm) registerForm.style.display = "flex";
    tabRegister.classList.add("active");
    tabLogin?.classList.remove("active");
  });

  modalOverlay?.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.style.display = "none";
    }
  });

  // Berfungsi untuk memblokir tombol protected jika belum ada login
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

  //  Berfungsi untul memvalidasi konfirmasi password
  if (registerForm) {
    registerForm.addEventListener("submit", function (e) {
      const password = document.getElementById("password").value;
      const confirmPassword = document.getElementById("confirmPassword").value;
      const errorMsg = document.getElementById("passwordError");

      if (password !== confirmPassword) {
        e.preventDefault();
        errorMsg.style.display = "block";
      } else {
        errorMsg.style.display = "none";
      }
    });
  }

  document.querySelectorAll(".toggle-password").forEach((toggleBtn) => {
    toggleBtn.addEventListener("click", function () {
      const input = this.parentElement.querySelector("input");
      if (!input) return;

      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";

      this.querySelector(".icon-eye-open").style.display = isHidden
        ? "none"
        : "inline";
      this.querySelector(".icon-eye-closed").style.display = isHidden
        ? "inline"
        : "none";
    });
  });
});
// Notifikasi pop-up (toast) dari flash messages Flask
if (typeof flashMessages !== "undefined" && flashMessages.length > 0) {
  flashMessages.forEach((msg) => showToast(msg));
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast-message";
  toast.textContent = message;

  const container = document.getElementById("toast-container");
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("show");
  }, 100);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => container.removeChild(toast), 500);
  }, 3000);
}
