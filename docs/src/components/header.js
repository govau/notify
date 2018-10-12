import React from 'react'
import styled from 'styled-components'

import dta from '../images/dta-wordmark.png'
import { Wrapper, PanelProvider } from './theme'
import Link from './link'

const Logo = styled.img`
  height: 4rem;
`

const Root = styled.header`
  background: ${props => props.theme.background};
  color: ${props => props.theme.content};
  width: 100%;
`

const Banner = styled.h1`
  display: inline-block;
  font-weight: normal;
  font-size: 1.8em;
  margin: 0 2rem;
`

const Heading = styled.div`
  margin: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 0;
`

const Nav = styled.nav``

const Navitems = styled.ul`
  list-style: none;
  margin: 0;
`

const Navitem = styled.li`
  display: inline-block;
  margin: 0 1rem;
`

export default ({ siteTitle }) => (
  <PanelProvider>
    <Root>
      <Wrapper>
        <Heading>
          <Link to="/">
            <Logo src={dta} />
            {false && <Banner>Notify</Banner>}
          </Link>
          <Nav>
            <Navitems>
              <Navitem>
                <Link to="/">Support</Link>
              </Navitem>
              <Navitem>
                <Link to="/">Features</Link>
              </Navitem>
              <Navitem>
                <Link to="/">Pricing</Link>
              </Navitem>
            </Navitems>
          </Nav>
        </Heading>
      </Wrapper>
    </Root>
  </PanelProvider>
)
