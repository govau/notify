if (process.env.ADMIN_SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.ADMIN_SENTRY_DSN,
    environment: process.env.ADMIN_SENTRY_ENV || ""
  });
}
