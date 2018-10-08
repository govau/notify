import React from 'react'
import styled, { ThemeProvider } from 'styled-components'

const theme = {
  background: '#FFFFFF',
  highlight: '#2483FF',
  content: '#0E3148',
  subtle: '#0e3148cc',
}

const panelTheme = {
  background: '#313131',
  content: '#FFFFFF',
}

const Provider = props => <ThemeProvider theme={theme} {...props} />

const PanelProvider = props => <ThemeProvider theme={panelTheme} {...props} />

const Wrapper = styled.section`
  margin: 0 auto;
  max-width: 120rem;
  width: 90%;
`

export { Provider as default, PanelProvider, theme, panelTheme, Wrapper }
