import React from 'react'
import { Link } from 'gatsby'
import styled from 'styled-components'

const Wrapper = styled.div`
  background: rebeccapurple;
  color: red;
  margin-bottom: 21.45rem;
`

const Content = styled.div`
  margin: 0 auto;
  max-width: 960px;
  padding: 1.45rem 1.0875rem;
`

const Heading = styled.h1`
  margin: 0;
`

const HeadingLink = styled(Link)`
  color: white;
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
