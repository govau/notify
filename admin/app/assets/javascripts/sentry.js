if (process.env.ADMIN_SENTRY_DSN) {
  Sentry.init({
    release: process.env.CIRCLE_SHA1 || undefined,
    dsn: process.env.ADMIN_SENTRY_DSN,
    environment: process.env.ADMIN_SENTRY_ENV || ""
  });
}
