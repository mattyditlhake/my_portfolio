console.log("script.js loaded");
document.addEventListener("DOMContentLoaded", () => {
  const counterValue = document.getElementById("visitor-count-value");
  const form = document.querySelector(".php-email-form");

  /*
   * Visitor counter flow:
   * 1. Read the current total from your own Vercel API route.
   * 2. Increment only once per browser for a limited time window.
   * 3. Render the value into the counter section between Skills and Contact.
   *
   * This keeps the count under your Vercel project instead of relying on an
   * external public counter service.
   */
  const visitorStorageKey = "portfolio_visit_counted_until_v1";
  const visitorCountWindowMs = 12 * 60 * 60 * 1000;

  async function loadVisitorCount() {
    if (!counterValue) return;

    const countedUntil = Number(localStorage.getItem(visitorStorageKey) || "0");
    const hasCountedVisit = Date.now() < countedUntil;
    const endpoint = hasCountedVisit ? "/api/visitors" : "/api/visitors";
    const requestOptions = hasCountedVisit
      ? { method: "GET" }
      : {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        };

    try {
      const response = await fetch(endpoint, requestOptions);
      if (!response.ok) {
        throw new Error("Unable to load visitor count right now.");
      }

      const data = await response.json();
      counterValue.textContent = Number(data.count || 0).toLocaleString();

      if (!hasCountedVisit) {
        localStorage.setItem(visitorStorageKey, String(Date.now() + visitorCountWindowMs));
      }
    } catch (error) {
      counterValue.textContent = "Unavailable";
      console.error("Visitor counter error:", error);
    }
  }

  loadVisitorCount();

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
