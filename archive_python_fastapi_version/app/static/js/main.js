document.addEventListener("DOMContentLoaded", () => {
  const messageInput = document.getElementById("message-input");

  // If on a page with a message input, focus it
  if (messageInput) {
    messageInput.focus();
  }

  convertTimesToLocal();

  document.body.addEventListener("htmx:afterSwap", (event) => {
    if (event.target.id === "comment-list") {
      // After HTMX updates the comment list, reset and refocus the input if present
      if (messageInput) {
        messageInput.value = "";
        messageInput.focus();
      }
      clearError();
      convertTimesToLocal();
    }
  });

  document.body.addEventListener("htmx:responseError", (event) => {
    const status = event.detail.xhr.status;
    if (status === 400) {
      displayError("Your message cannot be empty.");
    } else if (status === 403) {
      displayError("Invalid request token. Please reload the page and try again.");
    } else if (status === 429) {
      displayError("You have exceeded the rate limit. Please wait before posting again.");
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
        if (!isNaN(dateObj.getTime())) {
          const localTimeString = dateObj.toLocaleString([], {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            hour12: true,
          });
          elem.textContent = localTimeString;
        } else {
          elem.textContent = "Invalid Date";
        }
      }
    });
  }

  function displayError(msg) {
    let errorBox = document.getElementById("error-box");
    if (!errorBox) {
      errorBox = document.createElement("div");
      errorBox.id = "error-box";
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
