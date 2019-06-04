import React from 'react'
import styled from 'styled-components'
import Collapsible from './collapsible'
import P from './core/paragraph'

const Header = styled.div`
  background-color: #f3f5f5;
  padding: 1rem 2rem;

  display: flex;
  justify-content: space-between;
  align-items: center;

  & > * {
    display: inline-block;
  }

  ${props =>
    props.open
      ? '&:after { content: "↑ hide" }'
      : '&:after { content: "↓ show" }'}
`

const Content = styled.div`
  > * {
    padding: 0 2rem;
  }
  ${P} {
    margin-top: 1em;
  }
`

export const Panel = ({ label, children, defaultOpen }) => (
  <Collapsible
    open={defaultOpen}
    header={open => <Header open={open}>{label}</Header>}
  >
    <Content>{children}</Content>
  </Collapsible>
)
