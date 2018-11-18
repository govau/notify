const baseUrl = process.env.GATSBY_NOTIFY_BASE_URL || 'https://notify.gov.au'

const ensureOneLeadingSlash = input => `/${(input || '').replace(/^[/]*/, '')}`
const stripTrailingSlash = input => (input || '').replace(/[/]*$/, '')

const notifyUrl = relativePath =>
  `${stripTrailingSlash(baseUrl)}${ensureOneLeadingSlash(relativePath)}`

export { notifyUrl as default, stripTrailingSlash }
