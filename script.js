document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".php-email-form");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = {
      name: form.name.value,
      email: form.email.value,
      subject: form.subject.value,
      message: form.message.value,
    };

    const loading = form.querySelector(".loading");
    const error = form.querySelector(".error-message");
    const success = form.querySelector(".sent-message");

    loading.style.display = "block";
    error.style.display = "none";
    success.style.display = "none";

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      loading.style.display = "none";

      if (response.ok) {
        success.style.display = "block";
        form.reset();
      } else {
        error.style.display = "block";
        error.textContent = await response.text();
      }
    } catch (err) {
      loading.style.display = "none";
      error.style.display = "block";
      error.textContent = err.message;
    }
  });
});