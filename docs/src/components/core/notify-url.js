const baseUrl = process.env.NOTIFY_BASE_URL || 'https://notify.gov.au'

const stripLeadingSlash = input => {
  if (typeof input === 'string') return input.replace(/^[\/]*/, '')

  return input
}

const stripTrailingSlash = input => {
  if (typeof input === 'string') return input.replace(/[\/]*$/, '')

  return input
}

const notifyUrl = relativePath =>
  `${stripTrailingSlash(baseUrl)}/${stripLeadingSlash(relativePath)}`

export { notifyUrl as default, stripTrailingSlash }
