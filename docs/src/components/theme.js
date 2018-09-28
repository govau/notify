import React from 'react'
import { ThemeProvider } from 'styled-components'

const theme = {
  highlight: '#37C2F3',
  dark: '#062032',
  darker: '#062032',
  darkest: '#01090E66',
  content: '#0B3442',
  contentSubtle: '#0A3443B3',
  contentInverted: '#DBDCDD',
}

const Provider = props => <ThemeProvider theme={theme} {...props} />

export { Provider as default, theme }
