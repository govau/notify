import React, { createContext } from 'react'
import Select from 'react-select'

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
      <Select
        value={createLanguageOption(current)}
        options={languageOptions}
        onChange={({ value }) => changeLanguage(value)}
      />
    )}
  </Context.Consumer>
)

// Get the current language
const CurrentLanguage = ({ children }) => (
  <Context.Consumer>{({ current }) => children(current)}</Context.Consumer>
)

export { Languages as default, CurrentLanguage, Provider, getLanguageLabel }
