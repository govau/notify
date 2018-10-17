import React from 'react'
import { graphql } from 'gatsby'
import MDXRenderer from 'gatsby-mdx/mdx-renderer'

import Layout from './components/layout'
import { DynamicSidenav } from './components/sidenav'

export default ({ data }) => (
  <Layout sidenav={<DynamicSidenav />}>
    <MDXRenderer>{data.mdx.code.body}</MDXRenderer>
  </Layout>
)

export const pageQuery = graphql`
  query($id: String!) {
    mdx(id: { eq: $id }) {
      id
      code {
        body
      }
    }
  }
`
