const path = require('path')
const componentWithMDXScope = require('gatsby-mdx/component-with-mdx-scope')

const createMarkdownPages = ({ graphql, actions }) => {
  const { createPage } = actions
  const Markdown = path.resolve(`src/templates/markdown.js`)

  return graphql(`
    {
      allMarkdownRemark(
        sort: { order: DESC, fields: [frontmatter___date] }
        limit: 1000
      ) {
        edges {
          node {
            frontmatter {
              path
            }
          }
        }
      }
    }
  `).then(result => {
    if (result.errors) {
      return Promise.reject(result.errors)
    }

    result.data.allMarkdownRemark.edges.forEach(({ node }) => {
      createPage({
        path: node.frontmatter.path,
        component: Markdown,
        context: {}, // additional data can be passed via context
      })
    })
  })
}

const createMDXPages = ({ graphql, actions }) => {
  const { createPage } = actions
  return new Promise((resolve, reject) => {
    resolve(
      graphql(
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
          console.log(result.errors)
          reject(result.errors)
        }
        // Create blog posts pages.
        result.data.allMdx.edges.forEach(({ node }) => {
          createPage({
            path: `/${node.parent.sourceInstanceName}/${node.parent.name}`,
            component: componentWithMDXScope(
              path.resolve('./src/components/layout.js'),
              node.code.scope
            ),
            context: { id: node.id },
          })
        })
      })
    )
  })
}

exports.createPages = (...args) => {
  return Promise.all([createMarkdownPages(...args)])
}
