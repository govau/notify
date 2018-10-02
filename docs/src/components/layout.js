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
import './layout.css'

const Root = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`

const Main = styled(Wrapper)`
  flex: 1 0 auto;
  display: flex;
`

const Content = styled.div``

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
            <Sidenav />
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
