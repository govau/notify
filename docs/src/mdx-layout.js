import React from 'react'
import { graphql } from 'gatsby'
import MDXRenderer from 'gatsby-mdx/mdx-renderer'

import Layout from './components/layout'
import { DynamicSidenav } from './components/sidenav'
import { Provider as TOCProvider } from './components/table-of-contents'

// Get H2 links. this assumes an H1 is our first header, and gets all the
// subheadings below that. hacky.
const headingLinks = (pagePath, { items = [] }) =>
  items.length
    ? (items[0].items || []).map(({ url, title }) => ({
        url: `${pagePath}${url}`,
        title,
      }))
    : []

export default ({ data, location }) => (
  <TOCProvider
    value={headingLinks(data.mdx.fields.pagePath, data.mdx.tableOfContents)}
  >
    <Layout
      location={location}
      sidenav={<DynamicSidenav current={data.mdx.fields.pagePath} />}
    >
      <MDXRenderer>{data.mdx.code.body}</MDXRenderer>
    </Layout>
  </TOCProvider>
)

export const pageQuery = graphql`
  query($id: String!) {
    mdx(id: { eq: $id }) {
      id
      fields {
        pagePath
      }
      code {
        body
      }
      tableOfContents
      headings {
        value
        depth
      }
    }
  }
`
