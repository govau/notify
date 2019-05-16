// Gatsby builds the project in a node environment,
// where window and document don't exist. This utility
// allows the build to pass while granting access to
// these globals at runtime
export function getGlobals(cb) {
  const win = typeof window !== 'undefined' && window
  const doc = typeof document !== 'undefined' && document
  if (win && doc) {
    return cb({ win, doc })
  }
  return {}
}
