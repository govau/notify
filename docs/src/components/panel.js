import React from 'react'
import styled from 'styled-components'

const Details = styled.details``

const Summary = styled.summary`
  &::-webkit-details-marker {
    display: none;
  }

  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;

  & > * {
    display: inline-block;
  }

  &:after {
    content: '↓ more';
  }

  ${Details} [open] &:after {
    content: '↑ less';
  }
`

export const Panel = ({ label, children, open }) => (
  <Details open={open}>
    <Summary>{label}</Summary>
    {children}
  </Details>
)
