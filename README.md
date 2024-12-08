# DunamisMax.com

This is the source code for **DunamisMax.com**, now rewritten from a Python/Flask-based application into a Node.js/Express.js web application. The project leverages modern best practices, a secure configuration, and a clean codebase for ease of maintenance and scalability.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Security & Hardening](#security--hardening)
- [Deployment](#deployment)
- [License](#license)

## Overview

DunamisMax.com is a dark-themed, secure, and responsive website built using:

- **Node.js & Express.js** for server-side logic
- **EJS** as the templating engine
- **Nodemailer** for sending emails
- **CSRF protection**, **helmet**, and **express-rate-limit** for security
- **Winston** logging with daily rotation for robust logging
- **dotenv** for environment variables

## Features

- **Modern Web Stack:** Runs on Node.js and Express.js.
- **Security Best Practices:** Uses Helmet for enhanced HTTP headers, CSRF protection, and rate-limiting.
- **Clean UI & Dark Theme:** A cohesive dark theme using custom CSS variables.
- **Responsive Design:** Optimized for various screen sizes.
- **Modular & Extensible:** Organized routes, utilities, and views for easy maintenance.
- **Logging & Monitoring:** Winston-based logging with daily rotation.
- **EJS Templates:** Easy to maintain and extend server-rendered views.

## Project Structure

```bash
dunamismax.com/
└── dunamismax
    ├── public
    │   ├── css
    │   │   └── styles.css
    │   ├── images
    │   │   └── favicon.ico
    │   └── js
    │       └── scripts.js
    ├── routes
    │   └── main.js
    ├── utils
    │   ├── email.js
    │   └── logger.js
    ├── views
    │   ├── partials
    │   │   ├── footer.ejs
    │   │   └── header.ejs
    │   ├── 404.ejs
    │   ├── 500.ejs
    │   ├── blog.ejs
    │   ├── contact.ejs
    │   └── index.ejs
    ├── .env (not committed)
    ├── package.json
    └── server.js
```
