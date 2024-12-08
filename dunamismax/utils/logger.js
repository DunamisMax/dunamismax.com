const { createLogger, format, transports } = require("winston");

const logger = createLogger({
  level: "info",
  format: format.combine(
    format.timestamp({
      format: "YYYY-MM-DD HH:mm:ss",
    }),
    format.errors({ stack: true }),
    format.splat(),
    format.json()
  ),
  defaultMeta: { service: "dunamismax-service" },
  transports: [
    //
    // - Write all logs with level `error` and below to `error.log`
    //
    new transports.File({ filename: "logs/error.log", level: "error" }),
    //
    // - Write all logs with level `info` and below to `combined.log`
    //
    new transports.File({ filename: "logs/combined.log" }),
  ],
});

// If we're not in production then **ALSO** log to the `console`
if (process.env.NODE_ENV !== "production") {
  logger.add(
    new transports.Console({
      format: format.combine(format.colorize(), format.simple()),
    })
  );
}

module.exports = logger;
