import React from 'react'
import { Link } from 'gatsby'
import styled from 'styled-components'

const Wrapper = styled.div`
  background: #072a31;
  color: white;
  width: 100%;
`

const Content = styled.div`
  margin: 0 auto;
  padding: 1rem 2rem;
  max-width: 80rem;
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
