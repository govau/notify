import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'
import { StaticQuery, graphql } from 'gatsby'
import styled from 'styled-components'

import Header from './header'
import Footer from './footer'
import Providers from './providers'
import Sidenav from './sidenav'
import { SkipNavLink, SkipNavContent } from './skip-nav'
import { Wrapper } from './theme'
import { desktop } from './core/media'
import 'sanitize.css'
import './core/index.css'
import { removeLangFromHash } from '../utils/url'

const Root = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;

  color: ${props => props.theme.content};
`

const NavWrapper = styled.div`
  @media ${desktop} {
    flex: 0 0 33rem;
  }
`

const StickyNav = styled.div`
  margin: 2rem -2rem 0;

  @media ${desktop} {
    margin: 0 -2rem 0;
    position: sticky;
    top: 0;
    padding: 6rem 4rem;
    overflow-y: auto;
  }
`

const Main = styled(Wrapper)`
  flex: 1 0 auto;
  flex-direction: column;
  display: flex;
  position: relative;

  @media ${desktop} {
    flex-direction: row-reverse;
  }
`

const Content = styled.div`
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  flex-shrink: 1;
  flex-basis: auto;
  justify-content: flex-start;
  align-items: stretch;
  overflow: hidden;
  margin-bottom: 4rem;

  & > :first-child {
    margin-top: 1em;
  }

  @media ${desktop} {
    & > :first-child {
      margin-top: 6rem;
    }
  }
`

const Layout = ({ sidenav = <Sidenav />, children, location }) => {
  const getPageTitle = data => {
    const baseTitle = data.site.siteMetadata.title
    if (!location) {
      return baseTitle
    }

    const edge = data.mdxPages.edges.find(e =>
      e.page.fileAbsolutePath.includes(
        `${location.pathname.replace(/\//g, '')}.mdx`
      )
    )

    return `${edge.page.frontmatter.title} - ${baseTitle}`
  }

  useEffect(() => {
    const { hash, lang } = removeLangFromHash()
    // Only trigger scroll for hashes with a lang,
    // otherwise let browser handle scroll
    if (lang) {
      const target = document.querySelector(hash)
      target && target.scrollIntoView()
    }
  }, [])

  return (
    <Providers>
      <StaticQuery
        query={graphql`
          query SiteTitleQuery {
            site {
              siteMetadata {
                title
              }
            }
            mdxPages: allMdx {
              edges {
                page: node {
                  fileAbsolutePath
                  frontmatter {
                    title
                  }
                }
              }
            }
          }
        `}
        render={data => (
          <Root>
            <SkipNavLink href="#content">Skip to content</SkipNavLink>
            <SkipNavLink href="#nav">Skip to navigation</SkipNavLink>
            <Helmet
              title={getPageTitle(data)}
              meta={[
                { content: 'IE=edge', httpEquiv: 'X-UA-Compatible' },
                {
                  name: 'description',
                  content:
                    'Notify.gov.au lets you send emails and text messages to your users. Try it now if you work in Australian local, state or federal government.',
                },
              ]}
            >
              <html lang="en" />
            </Helmet>
            <Header siteTitle={data.site.siteMetadata.title} />
            <Main role="main">
              <SkipNavContent id="content" />
              <NavWrapper>
                <SkipNavContent id="nav" />
                <StickyNav>{sidenav}</StickyNav>
              </NavWrapper>
              <Content>{children}</Content>
            </Main>
            <Footer />
          </Root>
        )}
      />
    </Providers>
  )
}

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout
