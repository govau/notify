import React from 'react'
import styled from 'styled-components'
import Collapsible from './collapsible'

const BaseHeader = styled.div`
  background-color: #f3f5f5;
  padding: 1rem 2rem;

  * + & {
    margin-top: 2em;
  }
`

const Header = styled(BaseHeader)`
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

const Content = styled.div``

export const Panel = ({ label, children, defaultOpen }) => (
  <Collapsible
    open={defaultOpen}
    header={open => <Header open={open}>{label}</Header>}
  >
    <Content>{children}</Content>
  </Collapsible>
)

export const SimplePanel = ({ label, children }) => (
  <>
    <BaseHeader>{label}</BaseHeader>
    <Content>{children}</Content>
  </>
)
