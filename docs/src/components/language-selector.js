import React, { createContext } from 'react'
import styled, { css } from 'styled-components'

const Nav = styled.nav``

const LanguageLink = styled.span`
  cursor: pointer;
  font-size: 0.8em;

  ${props =>
    props.active
      ? css`
          text-decoration: underline;
          font-weight: bold;
        `
      : css``};
`

// spearate wrapper to get around props interpolation on LanguageLink
const NavLanguageLink = styled(LanguageLink)`
  & + & {
    margin-left: 1em;
  }
`

const Context = createContext({
  current: '',
  changeLanguage: language => {},
})

// Wrap everything in this to give access to a current language. You can nest
// this to give a sub-current-language.
class Provider extends React.Component {
  state = { current: this.props.initial || 'python' }

  changeLanguage = current => {
    this.setState({ current })
  }

  render() {
    return (
      <Context.Provider
        {...this.props}
        value={{
          current: this.state.current,
          changeLanguage: this.changeLanguage,
        }}
      />
    )
  }
}

const languages = {
  python: 'Python',
  java: 'Java',
  ruby: 'Ruby',
  node: 'Node.js',
  dotnet: '.NET',
}

const createLanguageOption = language => ({
  value: language,
  label: languages[language],
})

const languageOptions = Object.keys(languages).map(createLanguageOption)

// Pretty-print the current language
const getLanguageLabel = language => languages[language]

// Language selector. Pop this anywhere inside a provider context to allow for
// language selection.
const Languages = props => (
  <Context.Consumer>
    {({ current, changeLanguage }) => (
      <Nav>
        {languageOptions.map(({ value, label }) => (
          <NavLanguageLink
            active={value === current}
            key={label}
            onClick={e => changeLanguage(value)}
          >
            {label}
          </NavLanguageLink>
        ))}
      </Nav>
    )}
  </Context.Consumer>
)

// Get the current language
const CurrentLanguage = ({ children }) => (
  <Context.Consumer>{({ current }) => children(current)}</Context.Consumer>
)

export { Languages as default, CurrentLanguage, Provider, getLanguageLabel }
