const componentWithMDXScope = require('gatsby-mdx/component-with-mdx-scope')

const createMDXPagePath = node =>
  `/${node.parent.name}`

// Relate an MDX node with the page that we create below.
//
// Tried to create these nodes inside the createPages callback,
// but they don't have an effect unless we also create a node field here.
// for some reason.
// not sure.
const onCreateNode = ({ node, actions, getNode }) => {
  const { createNodeField } = actions

  if (node.internal.type !== 'Mdx') {
    return
  }

  createNodeField({
    node: node,
    name: 'pagePath',
    value: createMDXPagePath({ ...node, parent: getNode(node.parent) }),
  })
}

// Create a page for each MDX entry we find. You must configure this plugin with
// a layout to use as a basis for your MDX.
//
// This will fail if you don't have a source-filesystem thing feeding MDX files
// to gatsby-mdx.
//
// We also expose a "context.id" so that your layout file can look up the MDX
// node id and generate itself appropriately.
const createPages = (
  { graphql, actions, getNode, createContentDigest },
  options
) => {
  const { createPage, createNode, createNodeField } = actions

  return graphql(
    `
      {
        allMdx {
          edges {
            node {
              id
              parent {
                ... on File {
                  name
                  sourceInstanceName
                }
              }
              code {
                scope
              }
            }
          }
        }
      }
    `
  ).then(result => {
    if (result.errors) {
      throw result.errors
    }

    result.data.allMdx.edges.forEach(({ node }) => {
      createPage({
        path: createMDXPagePath(node),
        component: componentWithMDXScope(options.layout, node.code.scope),
        context: { id: node.id },
      })
    })
  })
}

// mdx pages don't seem to get access to our environment unless we do this sort
// of thing.
// makes all imports absolute instead of relative for MDX pages.
// not sure.
const onCreateWebpackConfig = ({ actions }, options) => {
  actions.setWebpackConfig({
    resolve: {
      modules: [options.srcDir, 'node_modules'],
    },
  })
}

module.exports = { createPages, onCreateWebpackConfig, onCreateNode }
