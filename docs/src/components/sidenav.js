import React from 'react'
import { StaticQuery, graphql } from 'gatsby'
import styled from 'styled-components'

import Link from './link'

const NavWrapper = styled.nav`
`

const NavList = styled.ul`
  list-style: none;
  margin: 0;
`

const NavItem = styled.li``

const Nav = props => (
  <NavWrapper {...props}>
    <NavList {...props} />
  </NavWrapper>
)

export default props => (
  <NavWrapper {...props}>
    <NavList>
      <NavItem>
        <Link to="/this-is-mdx">Getting started</Link>
      </NavItem>
      <NavItem>
        <Link to="/setup-client">Set up the client</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">Send a message</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">Get message status</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">Get a template</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">Get received text messages</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">Testing</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">API keys</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">Limits</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">Callbacks</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">API architecture</Link>
      </NavItem>
      <NavItem>
        <Link to="/this-is-mdx">Support</Link>
      </NavItem>
    </NavList>
  </NavWrapper>
)

export const dynamic = props => (
  <StaticQuery
    query={graphql`
      query GetThePages {
        pages: allSitePage {
          edges {
            page: node {
              path
            }
          }
        }
      }
    `}
    render={data => (
      <Nav>
        {data.pages.edges.map(({ page }, i) => (
          <NavItem key={i}>
            <Link to={page.path}>{page.path}</Link>
          </NavItem>
        ))}
      </Nav>
    )}
  />
)
