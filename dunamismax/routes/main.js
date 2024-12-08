// routes/main.js
// Main application routes

const express = require("express");
const router = express.Router();
const { body, validationResult } = require("express-validator");
const sendEmail = require("../utils/email");
const logger = require("../utils/logger");
const rateLimit = require("express-rate-limit");

// Contact form rate limiting
const contactFormLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,
  message:
    "Too many contact form submissions. Please try again after 15 minutes.",
  handler: (req, res) => {
    logger.warn(
      "Rate limit exceeded for IP: %s on route: %s",
      req.ip,
      req.originalUrl
    );
    req.flash(
      "error",
      "You have exceeded the maximum number of contact form submissions. Please try again later."
    );
    res.status(429).redirect("/contact");
  },
});

// Home Route
router.get("/", (req, res) => {
  logger.info("Home page accessed by user: %s", req.ip);
  res.render("index", { title: "Home", activePage: "home" });
});

// Blog Route
router.get("/blog", async (req, res) => {
  try {
    const posts = await getBlogPosts(); // Replace with real data fetching
    res.render("blog", { title: "Blog", activePage: "blog", posts });
    logger.info("Blog page accessed by user: %s", req.ip);
  } catch (error) {
    logger.error("Error fetching blog posts: %s", error.message);
    res
      .status(500)
      .render("500", { title: "500 - Server Error", activePage: "" });
  }
});

// Contact Route (GET)
router.get("/contact", (req, res) => {
  res.render("contact", {
    title: "Contact Us",
    activePage: "contact",
    form: {},
    errors: {},
    csrfToken: req.csrfToken(),
  });
});

// Contact Route (POST)
router.post(
  "/contact",
  contactFormLimiter,
  [
    body("name")
      .trim()
      .isLength({ min: 2, max: 100 })
      .withMessage("Name must be between 2 and 100 characters.")
      .escape(),
    body("email")
      .trim()
      .isEmail()
      .withMessage("Please enter a valid email address.")
      .normalizeEmail(),
    body("subject")
      .trim()
      .isLength({ min: 1, max: 150 })
      .withMessage("Subject is required and must be less than 150 characters.")
      .escape(),
    body("message")
      .trim()
      .isLength({ min: 10, max: 500 })
      .withMessage("Message must be between 10 and 500 characters.")
      .escape(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    const { name, email, subject, message } = req.body;

    if (!errors.isEmpty()) {
      const extractedErrors = {};
      errors.array().forEach((err) => {
        extractedErrors[err.param] = err.msg;
      });

      logger.warn(
        "Validation errors on contact form: IP %s, errors: %o",
        req.ip,
        extractedErrors
      );

      return res.status(422).render("contact", {
        title: "Contact Us",
        activePage: "contact",
        form: req.body,
        errors: extractedErrors,
        csrfToken: req.csrfToken(),
      });
    }

    try {
      // Send email
      const mailOptions = {
        from: `"${name}" <${email}>`,
        to: process.env.CONTACT_EMAIL || "contact@dunamismax.com",
        subject: `Contact Form Submission: ${subject}`,
        text: `
You have a new contact form submission.

Name: ${name}
Email: ${email}
Subject: ${subject}
Message:
${message}
        `,
      };

      await sendEmail(mailOptions);
      logger.info("Contact form submitted by %s <%s>", name, email);

      req.flash(
        "success",
        "Thank you for your message! We will get back to you soon."
      );
      res.redirect("/contact");
    } catch (error) {
      logger.error(
        "Error processing contact form from IP %s: %s",
        req.ip,
        error.message
      );
      req.flash(
        "error",
        "There was an error sending your message. Please try again later."
      );
      res.redirect("/contact");
    }
  }
);

// WebDAV Route (Unauthorized Access Handling)
router.all("/obsidian/*", (req, res) => {
  logger.warn(
    "Unauthorized access attempt to WebDAV by IP: %s, Path: %s",
    req.ip,
    req.originalUrl
  );
  res.status(403).send("Access to WebDAV is restricted.");
});

// Example: Fetching blog posts (Mock function)
async function getBlogPosts() {
  // Implement actual DB or API fetching here
  return [
    {
      slug: "first-blog-post",
      title: "First Blog Post",
      excerpt: "This is an excerpt from the first blog post...",
    },
    {
      slug: "second-blog-post",
      title: "Second Blog Post",
      excerpt: "This is an excerpt from the second blog post...",
    },
  ];
}

module.exports = router;
