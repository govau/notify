import React from 'react'
import { StaticQuery, graphql } from 'gatsby'
import styled, { css } from 'styled-components'

import Link from './link'

const NavWrapper = styled.nav``

const NavList = styled.ul`
  list-style: none;
  margin: 0;
  padding: 0;
`

const NavItem = styled.li`
  padding-left: 1em;
  & a {
    text-decoration: none;
  }

  ${props =>
    props.active
      ? css`
          border-left: 1px solid ${props.theme.highlight};
          & a {
            text-decoration: underline;
          }
        `
      : css``};
`

const SubNav = styled.ul`
  list-style: none;
  margin: 0;
  padding: 0;
`

const Nav = props => (
  <NavWrapper {...props}>
    <NavList {...props} />
  </NavWrapper>
)

export default props => (
  <NavWrapper {...props}>
    <NavList>
      <NavItem>
        <Link to="/getting-started">Getting started</Link>
      </NavItem>
      <NavItem>
        <SubNav>
          <NavItem>
            <Link to="/getting-started#creating-a-notify-client">
              Creating a notify client
            </Link>
          </NavItem>
          <NavItem active>
            <Link to="/getting-started#rolling-your-own-client">
              Rolling your own client
            </Link>
          </NavItem>
          <NavItem>
            <Link to="/getting-started#example-implementation">
              Example implementation
            </Link>
          </NavItem>
        </SubNav>
      </NavItem>

      <NavItem>
        <Link to="/installation">Installation</Link>
      </NavItem>
      <NavItem>
        <Link to="/setup-client">Set up the client</Link>
      </NavItem>
      <NavItem>
        <Link to="/sending-text-messages">Sending text messages</Link>
      </NavItem>
      <NavItem>
        <Link to="/sending-email-messages">Sending email messages</Link>
      </NavItem>
      <NavItem>
        <Link to="/check-available-templates">Check available templates</Link>
      </NavItem>

      <hr />

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
