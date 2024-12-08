// routes/main.js
const express = require("express");
const router = express.Router();
const { body, validationResult } = require("express-validator");
const sendEmail = require("../utils/email"); // Email utility
const logger = require("../utils/logger"); // Logger utility
const rateLimit = require("express-rate-limit");

// Define rate limiting rules for the contact form
const contactFormLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // limit each IP to 10 requests per windowMs
  message:
    "Too many contact form submissions from this IP, please try again after 15 minutes.",
  handler: (req, res /*next*/) => {
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
    // TODO: Fetch blog posts from a database or external API
    const posts = await getBlogPosts(); // Replace with your actual data fetching logic
    res.render("blog", { title: "Blog", activePage: "blog", posts });
    logger.info("Blog page accessed by user: %s", req.ip);
  } catch (error) {
    logger.error("Error fetching blog posts: %s", error.message);
    res
      .status(500)
      .render("500", { title: "500 - Server Error", activePage: "" });
  }
});

// Contact Routes
router.get("/contact", (req, res) => {
  res.render("contact", {
    title: "Contact Us",
    activePage: "contact",
    form: {},
    errors: {},
    csrfToken: req.csrfToken(), // Pass CSRF token to the view
  });
});

router.post(
  "/contact",
  contactFormLimiter, // Apply rate limiting specifically to the contact form
  [
    // Validation and Sanitization using express-validator
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
      // There are validation errors
      const extractedErrors = {};
      errors.array().map((err) => (extractedErrors[err.param] = err.msg));

      logger.warn(
        "Validation errors on contact form submission from IP %s: %o",
        req.ip,
        extractedErrors
      );

      return res.status(422).render("contact", {
        title: "Contact Us",
        activePage: "contact",
        form: req.body,
        errors: extractedErrors,
        csrfToken: req.csrfToken(), // Pass CSRF token to the view
      });
    }

    try {
      // Process the form data (e.g., send an email)
      const mailOptions = {
        from: `"${name}" <${email}>`, // Sender address
        to: process.env.CONTACT_EMAIL || "contact@dunamismax.com", // Receiver address
        subject: `Contact Form Submission: ${subject}`,
        text: `
You have a new contact form submission.

Name: ${name}
Email: ${email}
Subject: ${subject}
Message:
${message}
        `,
        // You can also send HTML content
        // html: `<p>You have a new contact form submission.</p><p><strong>Name:</strong> ${name}</p>...`,
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

// WebDAV Route (Handled by Apache2, restrict access to prevent redirect loops)
router.all("/obsidian/*", (req, res) => {
  logger.warn(
    "Unauthorized access attempt to WebDAV route by IP: %s, Path: %s",
    req.ip,
    req.originalUrl
  );
  res.status(403).send("Access to WebDAV is restricted.");
});

// Example function to fetch blog posts (Replace with actual implementation)
async function getBlogPosts() {
  // TODO: Implement actual data fetching logic
  // For demonstration, returning mock data
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
