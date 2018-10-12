import React from 'react'
import styled from 'styled-components'

import { PanelProvider, Wrapper } from './theme'
import dta from '../images/dta-wordmark.png'

const Logo = styled.img`
  height: 4rem;
`

const Root = styled.footer`
  background: ${props => props.theme.background};
  color: ${props => props.theme.content};
`

const Columns = styled.div`
  margin: 4rem 0;
  display: flex;
  justify-content: start;
  align-items: start;

  & > * + * {
    margin-left: 4rem;
  }
`

const Ul = styled.ul`
  margin-top: 0;
  margin-bottom: 0;
`

export default props => (
  <PanelProvider>
    <Root>
      <Wrapper>
        <Columns>
          <Logo src={dta} />

          <Ul>
            <li>these</li>
            <li>are</li>
            <li>items</li>
            <li>that</li>
            <li>go in the footer</li>
          </Ul>

          <Ul>
            <li>and even more</li>
            <li>footer</li>
            <li>items</li>
          </Ul>
        </Columns>
      </Wrapper>
    </Root>
  </PanelProvider>
)
