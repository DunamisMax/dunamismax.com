// server.js
// Entry point for the application

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
const logger = require("./utils/logger");

const app = express();

// Environment Variables
const PORT = process.env.PORT || 42069;
const SECRET_KEY = process.env.SECRET_KEY || "default-secret-key";
const NODE_ENV = process.env.NODE_ENV || "development";

// Trust proxy if behind a reverse proxy (like Apache/Nginx)
if (NODE_ENV === "production") {
  app.set("trust proxy", 1);
}

// Set EJS as the templating engine
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Security and CSP
app.use(
  helmet({
    contentSecurityPolicy: {
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
    },
    crossOriginEmbedderPolicy: false,
  })
);

// HTTP request logging via morgan -> winston
app.use(
  morgan(NODE_ENV === "production" ? "combined" : "dev", {
    stream: {
      write: (message) => logger.info(message.trim()),
    },
  })
);

// Gzip compression
app.use(compression());

// Body parsing
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

// Static files
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

// Session & Flash
app.use(
  session({
    secret: SECRET_KEY,
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: NODE_ENV === "production",
      httpOnly: true,
      maxAge: 1000 * 60 * 60 * 24,
      sameSite: "lax",
    },
  })
);
app.use(flash());

// Global Rate Limiting
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: "Too many requests, please try again later.",
});
app.use(globalLimiter);

// CSRF Protection
app.use(csrf());

// Inject global variables into views
app.use((req, res, next) => {
  res.locals.csrfToken = req.csrfToken();
  res.locals.success_messages = req.flash("success");
  res.locals.error_messages = req.flash("error");
  res.locals.user = req.session.user || null;
  next();
});

// Use main router
app.use("/", mainRouter);

// 404 Handler
app.use((req, res) => {
  res.status(404).render("404", { title: "404 - Page Not Found" });
});

// Global Error Handler
app.use((err, req, res, next) => {
  if (err.code === "EBADCSRFTOKEN") {
    logger.warn(
      "CSRF token validation failed for %s %s",
      req.method,
      req.originalUrl
    );
    req.flash("error", "Invalid CSRF token.");
    return res.redirect(req.get("Referrer") || "/");
  }

  logger.error("Unhandled Error: %o", err);

  // For non-operational errors, hide details from user
  res.status(500).render("500", { title: "500 - Server Error" });
});

// Graceful Shutdown
const shutdown = () => {
  logger.info("Shutting down server...");
  server.close(() => {
    logger.info("Server closed.");
    process.exit(0);
  });

  setTimeout(() => {
    logger.error("Forcing shutdown...");
    process.exit(1);
  }, 10000);
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

// Start Server
const server = app.listen(PORT, () => {
  logger.info(`Server is running on port ${PORT}`);
});
