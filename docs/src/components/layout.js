import React from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'
import { StaticQuery, graphql } from 'gatsby'
import styled from 'styled-components'

import Header from './header'
import Footer from './footer'
import Providers from './providers'
import './layout.css'

const Root = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`

const Main = styled.div`
  margin: 0 auto;
  padding: 1rem 2rem;
  max-width: 80rem;
  flex: 1 0 auto;
  width: 100%;
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
          <Main>{children}</Main>
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
