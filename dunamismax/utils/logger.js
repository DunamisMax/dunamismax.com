// utils/logger.js
// Winston logger configuration with daily rotate files

const { createLogger, format, transports } = require("winston");
const path = require("path");
const DailyRotateFile = require("winston-daily-rotate-file");

const logFormat = format.combine(
  format.timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
  format.errors({ stack: true }),
  format.splat(),
  format.json()
);

const logger = createLogger({
  level: "info",
  format: logFormat,
  defaultMeta: { service: "dunamismax-service" },
  transports: [
    new DailyRotateFile({
      filename: path.join(__dirname, "../logs/error-%DATE%.log"),
      datePattern: "YYYY-MM-DD",
      zippedArchive: true,
      maxSize: "20m",
      maxFiles: "14d",
      level: "error",
    }),
    new DailyRotateFile({
      filename: path.join(__dirname, "../logs/combined-%DATE%.log"),
      datePattern: "YYYY-MM-DD",
      zippedArchive: true,
      maxSize: "20m",
      maxFiles: "14d",
    }),
  ],
});

if (process.env.NODE_ENV !== "production") {
  logger.add(
    new transports.Console({
      format: format.combine(format.colorize(), format.simple()),
    })
  );
}

module.exports = logger;
