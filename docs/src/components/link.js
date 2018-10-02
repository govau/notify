import React from 'react'
import { Link } from 'gatsby'
import styled from 'styled-components'

export default styled(Link)`
  & {
    color: ${props => props.theme.tinted};
    text-decoration: none;
  }

  &:hover,
  &:focus,
  &:active {
    background-color: ${props => props.theme.highlight};
  }
`
