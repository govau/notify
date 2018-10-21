import React, { createContext } from 'react'
import Select from 'react-select'

const Context = createContext({
  current: '',
  changeLanguage: language => {},
})

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

const getLanguageLabel = language => languages[language]

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

const CurrentLanguage = ({ children }) => (
  <Context.Consumer>{({ current }) => children(current)}</Context.Consumer>
)

export { Languages as default, CurrentLanguage, Provider, getLanguageLabel }
