import React from 'react'
import { Link, graphql } from 'gatsby'

import Layout from '../components/layout'

export default ({ data }) => {
  return (
    <Layout>
      <h1>Hi people</h1>
      <p>Welcome to your new Gatsby site.</p>
      <p>Now go build something great.</p>
      <Link to="/page-2/">Go to page 2</Link>

      {data.markdown.edges.map(({ page }) => (
        <div>
          <Link to={page.frontmatter.path}>{page.frontmatter.title}</Link>
        </div>
      ))}
    </Layout>
  )
}

export const pageQuery = graphql`
  query {
    markdown: allMarkdownRemark {
      edges {
        page: node {
          frontmatter {
            title
            path
          }
        }
      }
    }
  }
`
