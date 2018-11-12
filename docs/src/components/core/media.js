import { css } from 'styled-components'

const min = size => `(min-width: ${size})`
const max = size => `(max-width: ${size})`

const breakpoint = size => (...args) => css`
  @media ${size} {
    ${css(...args)};
  }
`

const mobile = max('40em')
const desktop = min('64em')
const nondesktop = max('64em')

export { mobile, desktop, nondesktop }

export default {
  mobile: breakpoint(mobile),
  desktop: breakpoint(desktop),
  nondesktop: breakpoint(nondesktop),
}
