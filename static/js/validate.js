function showError(input, message) {
  const errorEl = document.getElementById(input.id + "-error");
  if (errorEl) errorEl.textContent = message || "";
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function setupRegisterForm() {
  const form = document.getElementById("register-form");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    const name = form.querySelector("#name");
    const email = form.querySelector("#email");
    const password = form.querySelector("#password");
    const confirmPassword = form.querySelector("#confirm_password");

    let hasError = false;

    showError(name, "");
    showError(email, "");
    showError(password, "");
    showError(confirmPassword, "");

    if (!name.value.trim()) {
      showError(name, "Name is required");
      hasError = true;
    }
    if (!email.value.trim()) {
      showError(email, "Email is required");
      hasError = true;
    } else if (!EMAIL_RE.test(email.value.trim())) {
      showError(email, "Please enter a valid email");
      hasError = true;
    }
    if (!password.value) {
      showError(password, "Password is required");
      hasError = true;
    }
    if (!confirmPassword.value) {
      showError(confirmPassword, "Confirm password is required");
      hasError = true;
    }
    if (password.value && confirmPassword.value && password.value !== confirmPassword.value) {
      showError(confirmPassword, "Passwords do not match");
      hasError = true;
    }

    if (hasError) event.preventDefault();
  });
}

function setupLoginForm() {
  const form = document.getElementById("login-form");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    const email = form.querySelector("#email");
    const password = form.querySelector("#password");

    let hasError = false;

    showError(email, "");
    showError(password, "");

    if (!email.value.trim()) {
      showError(email, "Email is required");
      hasError = true;
    }
    if (!password.value) {
      showError(password, "Password is required");
      hasError = true;
    }

    if (hasError) event.preventDefault();
  });
}

function setupAddTodoForm() {
  const form = document.getElementById("add-form");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    const title = form.querySelector("#title");
    showError(title, "");

    const value = title.value.trim();
    let hasError = false;

    if (!value) {
      showError(title, "Title is required");
      hasError = true;
    } else if (title.value.length > 200) {
      showError(title, "Title is too long");
      hasError = true;
    }

    if (hasError) event.preventDefault();
  });
}

function setupEditTodoForms() {
  document.querySelectorAll(".edit-form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      const input = form.querySelector(".todo-title-input");
      const value = input.value.trim();

      if (!value || input.value.length > 200) {
        event.preventDefault();
        alert(!value ? "Title is required" : "Title is too long");
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  setupRegisterForm();
  setupLoginForm();
  setupAddTodoForm();
  setupEditTodoForms();
});
