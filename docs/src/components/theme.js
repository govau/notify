import React from 'react'
import styled, { ThemeProvider } from 'styled-components'

const theme = {
  highlight: '#37C2F3',
  dark: '#062032',
  darker: '#01090E66',
  darkest: '#121212',
  subtle: '#F2F6F7',
  content: '#0B3442',
  contentSubtle: '#0A3443B3',
  contentInverted: '#DBDCDD',
}

const Provider = props => <ThemeProvider theme={theme} {...props} />

const Wrapper = styled.section`
  margin: 0 auto;
  max-width: 120rem;
  width: 100%;
`

export { Provider as default, theme, Wrapper }
