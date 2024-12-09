document.addEventListener("DOMContentLoaded", () => {
  const messageInput = document.getElementById("message-input");
  if (messageInput) {
    messageInput.focus();
  }

  // Convert all comment times to local time
  convertTimesToLocal();

  // Existing HTMX event listeners remain the same...
  document.body.addEventListener("htmx:afterSwap", (event) => {
    if (event.target.id === "comment-list") {
      if (messageInput) {
        messageInput.value = "";
        messageInput.focus();
      }
      clearError();
      convertTimesToLocal(); // Reconvert times after new comments load
    }
  });

  document.body.addEventListener("htmx:responseError", (event) => {
    if (event.detail.xhr.status === 400) {
      displayError("Your message cannot be empty.");
    } else {
      displayError("An unexpected error occurred. Please try again.");
    }
  });

  function convertTimesToLocal() {
    const timeElements = document.querySelectorAll(".comment-time");
    timeElements.forEach((elem) => {
      const utcTime = elem.getAttribute("datetime");
      if (utcTime) {
        const dateObj = new Date(utcTime);
        // Convert to local time string
        const localTimeString = dateObj.toLocaleString([], {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
          hour12: true,
        });
        elem.textContent = localTimeString;
      }
    });
  }

  function displayError(msg) {
    let errorBox = document.getElementById("error-box");
    if (!errorBox) {
      errorBox = document.createElement("div");
      errorBox.id = "error-box";
      errorBox.style.color = "#ff7575";
      errorBox.style.margin = "1rem 0";
      errorBox.style.textAlign = "center";
      const form = document.querySelector(".post-form");
      if (form) {
        form.insertAdjacentElement("afterend", errorBox);
      }
    }
    errorBox.textContent = msg;
    if (messageInput) {
      messageInput.classList.add("error");
    }
  }

  function clearError() {
    const errorBox = document.getElementById("error-box");
    if (errorBox) {
      errorBox.remove();
    }
    if (messageInput) {
      messageInput.classList.remove("error");
    }
  }
});
