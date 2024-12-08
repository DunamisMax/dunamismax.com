// server.js
const express = require("express");
const path = require("path");
const mainRouter = require("./routes/main");
const bodyParser = require("body-parser");
const session = require("express-session");
const flash = require("express-flash");

const app = express();

// Set EJS as the templating engine
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Middleware for parsing form data
app.use(bodyParser.urlencoded({ extended: false }));

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, "public")));

// Session middleware for flash messages
app.use(
  session({
    secret: "your-secret-key", // Replace with a secure key in production
    resave: false,
    saveUninitialized: true,
  })
);

// Flash middleware
app.use(flash());

// Global variables for flash messages
app.use((req, res, next) => {
  res.locals.success_messages = req.flash("success");
  res.locals.error_messages = req.flash("error");
  next();
});

// Use the main router for all routes
app.use("/", mainRouter);

// Start the server
const PORT = process.env.PORT || 42069;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
