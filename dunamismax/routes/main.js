// routes/main.js
const express = require("express");
const router = express.Router();

// Utility function to validate email
function validateEmail(email) {
  const re =
    /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@(([^<>()[\]\\.,;:\s@"]+\.)+[^<>()[\]\\.,;:\s@"]{2,})$/i;
  return re.test(String(email).toLowerCase());
}

// Home Route
router.get("/", (req, res) => {
  res.render("index", { title: "Dunamis Max" });
});

// Blog Route
router.get("/blog", (req, res) => {
  res.render("blog", { title: "Blog" });
});

// Contact Routes
router.get("/contact", (req, res) => {
  res.render("contact", { title: "Contact Us", form: {}, errors: {} });
});

router.post("/contact", (req, res) => {
  const { name, email, subject, message } = req.body;
  const errors = {};

  // Validate Name
  if (!name || name.trim().length < 2 || name.trim().length > 100) {
    errors.name = "Name must be between 2 and 100 characters.";
  }

  // Validate Email
  if (!email || !validateEmail(email) || email.length > 120) {
    errors.email = "Please enter a valid email address.";
  }

  // Validate Subject
  if (!subject || subject.trim().length > 150) {
    errors.subject =
      "Subject is required and must be less than 150 characters.";
  }

  // Validate Message
  if (!message || message.trim().length < 10 || message.trim().length > 500) {
    errors.message = "Message must be between 10 and 500 characters.";
  }

  if (Object.keys(errors).length > 0) {
    res.render("contact", { title: "Contact Us", form: req.body, errors });
  } else {
    // TODO: Process the form data (e.g., send an email or store in database)
    req.flash(
      "success",
      "Thank you for your message! We will get back to you soon."
    );
    res.redirect("/contact");
  }
});

module.exports = router;
