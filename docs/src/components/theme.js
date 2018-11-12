import React from 'react'
import styled, { ThemeProvider } from 'styled-components'

import { desktop } from './core/media'

const colours = {
  prettyBlue: '#2483FF',
}

const theme = {
  colours,
  background: '#FFFFFF',
  highlight: '#50C2EE',
  content: '#414141',
  subtle: '#414141',
  link: '#007099',
}

const panelTheme = {
  background: '#313131',
  content: '#FFFFFF',
  link: '#FFFFFF',
}

const Provider = props => <ThemeProvider theme={theme} {...props} />

const PanelProvider = props => <ThemeProvider theme={panelTheme} {...props} />

const Wrapper = styled.section`
  margin: 0 auto;
  padding: 0 2rem;
  max-width: 96rem;
  width: 100%;

  @media ${desktop} {
    padding: 0;
  }
`

export { Provider as default, PanelProvider, theme, panelTheme, Wrapper }
