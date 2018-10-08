import React from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'
import { StaticQuery, graphql } from 'gatsby'
import styled from 'styled-components'

import Header from './header'
import Footer from './footer'
import Providers from './providers'
import Sidenav from './sidenav'
import { Wrapper } from './theme'
import 'sanitize.css'
import './core/index.css'

const Root = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;

  color: ${props => props.theme.content};
`

const NavWrapper = styled.div`
  flex: 0 0 300px;
`

const StickyNav = styled.div`
  position: sticky;
  top: 0;
  padding: 4rem;
  overflow-y: auto;
`

const Main = styled(Wrapper)`
  flex: 1 0 auto;
  display: flex;
  position: relative;
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
`

const Layout = ({ children }) => (
  <Providers>
    <StaticQuery
      query={graphql`
        query SiteTitleQuery {
          site {
            siteMetadata {
              title
            }
          }
        }
      `}
      render={data => (
        <Root>
          <Helmet
            title={data.site.siteMetadata.title}
            meta={[
              { name: 'description', content: 'Sample' },
              { name: 'keywords', content: 'sample, something' },
            ]}
          >
            <html lang="en" />
          </Helmet>
          <Header siteTitle={data.site.siteMetadata.title} />
          <Main>
            <Content>{children}</Content>
            <NavWrapper>
              <StickyNav>
                <Sidenav />
              </StickyNav>
            </NavWrapper>
          </Main>
          <Footer />
        </Root>
      )}
    />
  </Providers>
)

Layout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default Layout
