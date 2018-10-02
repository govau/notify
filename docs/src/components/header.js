import React from 'react'
import { Link } from 'gatsby'
import styled from 'styled-components'

import { Wrapper } from './theme'

const Root = styled.div`
  background: ${props => props.theme.darkest};
  color: ${props => props.theme.contentInverted};
  width: 100%;
`

const Heading = styled.div`
  margin: 0;
`

const HeadingLink = styled(Link)`
  color: ${props => props.theme.contentInverted};
  text-decoration: none;
`

export default ({ siteTitle }) => (
  <Root>
    <Wrapper>
      <Heading>
        <HeadingLink to="/">{siteTitle}</HeadingLink>
      </Heading>
    </Wrapper>
  </Root>
)
