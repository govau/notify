import React from 'react'
// import SyntaxHighligher from 'react-syntax-highlighter'
import styled from 'styled-components'

const Wrapper = styled.div`
  background: ${props => props.theme.darker};
  color: ${props => props.theme.contentInverted};
`

const Heading = styled.header`
  background: ${props => props.theme.darkest};
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  font-family: 'system-ui';
`

const Language = styled.span`
  color: ${props => props.theme.highlight};
`

const SyntaxHighligher = styled.div`
  background: #01090e;
  padding: 1rem;
`

export default props => (
  <Wrapper>
    <Heading>
      <span>{'</>'} Initialising your client</span>
      <Language>OCaml</Language>
    </Heading>
    <SyntaxHighligher {...props} />
  </Wrapper>
)
