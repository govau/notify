import React from 'react'
import styled from 'styled-components'

const Details = styled.details`
  & > * {
    padding: 0 2rem;
  }
`

const Summary = styled.summary`
  background-color: #f3f5f5;

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
    content: '↓ show';
  }

  ${Details}[open] &:after {
    content: '↑ hide';
  }
`

export const Panel = ({ label, children, open }) => (
  <Details open={open}>
    <Summary>{label}</Summary>
    {children}
  </Details>
)
