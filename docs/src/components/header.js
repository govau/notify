import React from 'react'
import { Link } from 'gatsby'
import styled from 'styled-components'

const Wrapper = styled.div`
  background: ${props => props.theme.darkest};
  color: ${props => props.theme.contentInverted};
  width: 100%;
`

const Content = styled.div`
  margin: 0 auto;
  padding: 1rem 2rem;
  max-width: 80rem;
`

const Heading = styled.div`
  margin: 0;
`

const HeadingLink = styled(Link)`
  color: ${props => props.theme.contentInverted};
  text-decoration: none;
`

export default ({ siteTitle }) => (
  <Wrapper>
    <Content>
      <Heading>
        <HeadingLink to="/">{siteTitle}</HeadingLink>
      </Heading>
    </Content>
  </Wrapper>
)
