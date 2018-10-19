import React from 'react'
import styled from 'styled-components'

export const SkipNavLink = styled.a`
  border: 0;
  clip: rect(0 0 0 0);
  height: 1px;
  width: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  position: absolute;
  color: ${props => props.theme.content};

  &:focus {
    padding: 1rem;
    position: fixed;
    top: 10px;
    left: 10px;
    background-color: ${props => props.theme.highlight};
    z-index: 1;
    width: auto;
    height: auto;
    clip: auto;
  }
`

export const SkipNavContent = props => <div {...props} />
