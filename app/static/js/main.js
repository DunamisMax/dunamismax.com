document.addEventListener("DOMContentLoaded", () => {
  const messageInput = document.getElementById("message-input");

  // Focus the message input on load.
  if (messageInput) {
    messageInput.focus();
  }

  // Listen for htmx events to handle errors gracefully
  document.body.addEventListener("htmx:responseError", (event) => {
    // This event is triggered if the server returns an error (like 400)
    if (event.detail.xhr.status === 400) {
      // Show an error message to the user
      displayError("Your message cannot be empty.");
    } else {
      displayError("An unexpected error occurred. Please try again.");
    }
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    // After a successful swap (like after posting a comment), refocus the input and clear it
    if (event.target.id === "comment-list") {
      if (messageInput) {
        messageInput.value = "";
        messageInput.focus();
      }
      clearError();
    }
  });

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

    // Add visual indication to input
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
