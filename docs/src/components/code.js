import React from 'react'
import SyntaxHighligher from 'react-syntax-highlighter'
import styled from 'styled-components'
import { tomorrowNight } from 'react-syntax-highlighter/styles/hljs'

const Wrapper = styled.div`
  background: ${props => props.theme.dark};
  color: ${props => props.theme.contentInverted};
`

const Heading = styled.header`
  background: ${props => props.theme.darker};
  display: flex;
  justify-content: space-between;
  padding: 2rem;
`

const Language = styled.span`
  color: ${props => props.theme.colours.prettyBlue};
`

const Content = styled.div`
  padding: 2rem;
  padding-bottom: 3rem;
`

export default props => (
  <Wrapper>
    <Heading>
      <span>{'</>'} Initialising your client</span>
      <Language>{props.language}</Language>
    </Heading>
    <Content>
      <SyntaxHighligher
        style={tomorrowNight}
        customStyle={{
          background: 'none',
          margin: '0',
          padding: '0',
          overflowX: 'scroll',
        }}
        {...props}
      />
    </Content>
  </Wrapper>
)
