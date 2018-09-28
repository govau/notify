import React from 'react'
import styled from 'styled-components'

const Wrapper = styled.div`
  background: #072a31;
  color: white;
  width: 100%;
`

const Content = styled.div`
  margin: 0 auto;
  padding: 1rem 2rem;
  max-width: 92rem;
`

const Heading = styled.h1`
  margin: 0;
`

export default ({ siteTitle }) => (
  <Wrapper>
    <Content>
      <Heading>Hello there! i am a footer. enjoy it.</Heading>
    </Content>
  </Wrapper>
)
