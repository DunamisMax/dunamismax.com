// server.js

// Load environment variables from .env
require("dotenv").config();

const express = require("express");
const path = require("path");
const mainRouter = require("./routes/main");
const session = require("express-session");
const flash = require("express-flash");
const helmet = require("helmet");
const morgan = require("morgan");
const compression = require("compression");
const csrf = require("csurf");
const rateLimit = require("express-rate-limit");
const logger = require("./utils/logger"); // Import the logger

const app = express();

// Environment Variables
const PORT = process.env.PORT || 42069;
const SECRET_KEY = process.env.SECRET_KEY || "default-secret-key"; // Replace with a strong secret in production
const NODE_ENV = process.env.NODE_ENV || "development";

// Trust proxy if behind a proxy (e.g., Apache2)
if (NODE_ENV === "production") {
  app.set("trust proxy", 1); // Trust first proxy
}

// Set EJS as the templating engine
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Middleware Setup

// Security HTTP headers with Content Security Policy
app.use(helmet());

// Content Security Policy (CSP) configuration
app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "https://unpkg.com/htmx.org"],
      styleSrc: ["'self'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:"],
      connectSrc: ["'self'"],
      frameSrc: ["'self'"],
      objectSrc: ["'none'"],
      upgradeInsecureRequests: [],
    },
  })
);

// HTTP request logger with winston
app.use(
  morgan(NODE_ENV === "production" ? "combined" : "dev", {
    stream: {
      write: (message) => logger.info(message.trim()), // Log using winston
    },
  })
);

// Gzip compression
app.use(compression());

// Body parsing middleware (replacing body-parser)
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

// Serve static files from the 'public' directory with enhanced security
app.use(
  express.static(path.join(__dirname, "public"), {
    dotfiles: "ignore",
    etag: false,
    extensions: ["html", "css", "js"],
    index: false,
    maxAge: "1d",
    redirect: false,
  })
);

// Session middleware for flash messages
app.use(
  session({
    secret: SECRET_KEY,
    resave: false,
    saveUninitialized: false, // Prevents saving uninitialized sessions
    cookie: {
      secure: NODE_ENV === "production", // Ensures cookies are only sent over HTTPS
      httpOnly: true, // Prevents client-side JavaScript from accessing the cookie
      maxAge: 1000 * 60 * 60 * 24, // 1 day
      sameSite: "lax", // CSRF protection
    },
  })
);

// Flash middleware
app.use(flash());

// Rate Limiting Middleware (Global)
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: "Too many requests from this IP, please try again after 15 minutes.",
});

app.use(globalLimiter);

// CSRF Protection Middleware
const csrfProtection = csrf();

// Initialize CSRF protection after the session middleware
app.use(csrfProtection);

// Pass CSRF token and other global variables to all views
app.use((req, res, next) => {
  res.locals.csrfToken = req.csrfToken();
  res.locals.success_messages = req.flash("success");
  res.locals.error_messages = req.flash("error");
  res.locals.user = req.session.user || null; // Example: if you have user sessions
  next();
});

// Use the main router for all routes
app.use("/", mainRouter);

// Error Handling Middleware

// 404 Not Found Handler
app.use((req, res, next) => {
  res.status(404).render("404", { title: "404 - Page Not Found" });
});

// Global Error Handler
app.use((err, req, res, next) => {
  if (err.code === "EBADCSRFTOKEN") {
    // CSRF token validation failed
    logger.warn(
      "CSRF token validation failed for %s %s",
      req.method,
      req.originalUrl
    );
    req.flash("error", "Invalid CSRF token.");
    return res.redirect(req.get("Referrer") || "/"); // Updated redirect
  }

  // Log the error
  logger.error("Unhandled Error: %o", err);

  // Determine if the error is operational or programming error
  const isOperational = err.isOperational || false;

  // Respond with a generic message for non-operational errors
  if (!isOperational) {
    res.status(500).render("500", { title: "500 - Server Error" });
  } else {
    res
      .status(err.status || 500)
      .render("500", { title: "500 - Server Error", message: err.message });
  }
});

// Graceful Shutdown
const shutdown = () => {
  logger.info("Shutting down server...");
  server.close(() => {
    logger.info("Server closed.");
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    logger.error("Forcing shutdown...");
    process.exit(1);
  }, 10000);
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

// Start the server
const server = app.listen(PORT, () => {
  logger.info(`Server is running on port ${PORT}`);
});
