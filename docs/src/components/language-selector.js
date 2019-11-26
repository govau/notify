import React, { createContext, Fragment } from 'react'
import styled from 'styled-components'
import Select from 'react-select'
import PropTypes from 'prop-types'

import { H3 } from './core/heading'
import { languages } from '../config'

const Nav = styled.nav`
  display: flex;
  border-bottom: 4px solid #313131;

  & > * + * {
    margin-left: 2px;
  }
`

const NavLanguageLink = styled.button`
  cursor: pointer;
  border: 0;
  background-color: #e8fafc;

  padding: 1em 1em;
  flex: 1 1 auto;
  text-align: center;
`

// This component is specifically a `div` and not a `button` because of some
// issues we've got that seem to go pretty deep.
//
// Gatsby will do an initial server render with no access to window. When that
// happens we have no active tabs and no active styles are applied. On initial
// client load, the language provider kicks in and reads language from the
// browser URL. It then might pick up that a tab should be active, but for some
// reason a proper re-render doesn't occur. React thinks that we've done the
// render, but no styles are applied. This happens even if we aren't using
// styled components (just plain react); it also happens if we set a
// timeout and re-read the active language after the initial render.
//
// The only surefire way we've found to trigger a dom update is to swap out
// to a new element type -- which is why this is a div instead of a button.
const ActiveNavLanguageLink = styled.div`
  cursor: pointer;
  border: 0;
  text-decoration: underline;
  font-weight: bold;
  background-color: #313131;
  color: white;

  padding: 1em 1em;
  flex: 1 1 auto;
  text-align: center;
`

const createLanguageOption = language => ({
  value: language,
  label: languages[language],
})

const languageOptions = Object.keys(languages)
  .sort()
  .map(createLanguageOption)

// Pretty-print the current language
const getLanguageLabel = language => languages[language]

const Context = createContext({
  current: '',
  changeLanguage: language => {},
})

// Wrap everything in this to give access to a current language. You can nest
// this to give a sub-current-language.
class Provider extends React.Component {
  state = { current: this.props.initial || languageOptions[0].value }

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

// Language selector. Pop this anywhere inside a provider context to allow for
// language selection.
const Languages = props => (
  <Context.Consumer>
    {({ current, changeLanguage }) => (
      <Fragment>
        <H3>Select language</H3>
        <Nav>
          {languageOptions
            .filter(({ value }) =>
              !props.only ? true : props.only.includes(value)
            )
            .map(({ value, label }) =>
              value === current ? (
                <ActiveNavLanguageLink
                  key={label}
                  tabIndex="0"
                  onClick={() => {
                    changeLanguage(value)
                    props.onChange(value)
                  }}
                >
                  {label}
                </ActiveNavLanguageLink>
              ) : (
                <NavLanguageLink
                  key={label}
                  onClick={() => {
                    changeLanguage(value)
                    props.onChange(value)
                  }}
                >
                  {label}
                </NavLanguageLink>
              )
            )}
        </Nav>
      </Fragment>
    )}
  </Context.Consumer>
)

Languages.propTypes = {
  /** Called when a language is selected. Selected language is passed as only parameter. */
  onChange: PropTypes.func,
  only: PropTypes.array,
}

Languages.defaultProps = {
  onChange: () => {},
}

const Selector = props => (
  <Context.Consumer>
    {({ current, changeLanguage }) => (
      <Select
        isSearchable={false}
        styles={{
          control: provided => ({
            ...provided,
          }),
        }}
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

export {
  Languages as default,
  Selector,
  CurrentLanguage,
  Provider,
  getLanguageLabel,
}
