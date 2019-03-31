import React from 'react'
import styled from 'styled-components'

let counter = 0

const generateId = () => counter++

const Header = styled.button`
  border: none;
  background: none;
  box-shadow: none;
  display: block;
  padding: 0;
  margin: 0;
`

const Content = styled.div`
  display: ${props => (props.open ? 'block' : 'none')};
`

/**
 * @param {boolean}   open    sets default open state
 * @param {function}  header  render function for collapsible header. accepts `open` as a param.
 */
class Collapsible extends React.Component {
  static defaultProps = {
    open: false,
  }

  constructor(props) {
    super(props)
    this.state = {
      open: props.open,
    }
    const id = generateId()
    this.headerId = `collapsible-header-${id}`
    this.contentId = `collapsible-content-${id}`
  }

  toggleCollapsible = () => {
    this.setState(prevState => ({
      open: !prevState.open,
    }))
  }

  render() {
    const { header, children } = this.props
    const { open } = this.state
    const headerProps = {
      id: this.headerId,
      'aria-expanded': open,
      'aria-controls': this.contentId,
      onClick: this.toggleCollapsible,
    }
    const contentProps = {
      id: this.contentId,
      role: 'region',
      'aria-labelledby': this.headerId,
      open,
    }
    return (
      <>
        <Header {...headerProps}>{header(open)}</Header>
        <Content {...contentProps}>{children}</Content>
      </>
    )
  }
}

export default Collapsible
