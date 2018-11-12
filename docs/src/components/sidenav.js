import React, { Fragment } from 'react'
import { StaticQuery, graphql } from 'gatsby'
import styled, { css } from 'styled-components'

import LanguageSelector from './language-selector'
import Link from './link'

const NavWrapper = styled.nav`
  line-height: 1.8em;
`

const NavList = styled.ol`
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

const NavLink = ({ to, children, ...props }) => (
  <NavItem {...props}>
    <Link to={to}>{children}</Link>
  </NavItem>
)

const NestedNav = props => (
  <NavItem>
    <NavList {...props} />
  </NavItem>
)

const MAXDepth = 2

const Contents = ({
  container: Container = NestedNav,
  pagePath,
  items = [],
  depth = 0,
}) =>
  items.length && depth < MAXDepth ? (
    <Container>
      {items.map(item => (
        <Fragment key={item.url}>
          <NavLink to={`${pagePath}${item.url}`}>{item.title}</NavLink>
          <Contents pagePath={pagePath} items={item.items} depth={depth + 1} />
        </Fragment>
      ))}
    </Container>
  ) : null

export const DynamicSidenav = ({ current, ...props }) => (
  <StaticQuery
    query={graphql`
      {
        pages: allSitePage {
          edges {
            page: node {
              path
            }
          }
        }

        mdxPages: allMdx {
          edges {
            page: node {
              id
              tableOfContents
              fields {
                pagePath
              }
              headings {
                value
                depth
              }
              frontmatter {
                title
              }
            }
          }
        }
      }
    `}
    render={data => {
      const Option = ({ children }) => {
        const edge = data.mdxPages.edges.find(
          ({ page }) => page.fields.pagePath === children
        )

        if (!edge) {
          console.warn(`couldnt find page for option ${children}`)
          return null
        }

        const { page } = edge

        return page.frontmatter.title ? (
          <NavLink
            active={current === page.fields.pagePath}
            to={page.fields.pagePath}
          >
            {page.frontmatter.title}
          </NavLink>
        ) : (
          <NavLink
            active={current === page.fields.pagePath}
            to={page.fields.pagePath}
          >
            {page.headings[0].value}
          </NavLink>
        )
      }

      return (
        <Fragment>
          <LanguageSelector />
          <NavWrapper>
            <NavList>
              <Option>/installation</Option>
              <Option>/setup-client</Option>
              <Option>/sending-email-messages</Option>
              <Option>/sending-text-messages</Option>
              <Option>/check-available-templates</Option>
            </NavList>
          </NavWrapper>
        </Fragment>
      )
    }}
  />
)

export default DynamicSidenav
