import React from 'react'
import { Link } from 'gatsby'
import styled, { css } from 'styled-components'

const styles = css`
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

export default styled(Link)`
  ${styles};
`

const ExternalX = styled.a`
  ${styles};
`

const blankProps = { target: '_blank', rel: 'noopener noreferrer' }

export const External = ({ blank, ...props }) => (
  <ExternalX {...(blank ? blankProps : null)} {...props} />
)
