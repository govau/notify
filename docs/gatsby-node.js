const path = require('path')

// mdx pages don't get access to our environment unless we do this sort
// of thing.
//
// makes all imports absolute instead of relative for MDX pages.
// gross.
//
// https://github.com/ChristopherBiscardi/gatsby-mdx/issues/176
// https://github.com/ChristopherBiscardi/gatsby-mdx/issues/133
// https://github.com/ChristopherBiscardi/gatsby-mdx/issues/130
const onCreateWebpackConfig = ({ actions }) => {
  actions.setWebpackConfig({
    resolve: {
      modules: [path.resolve(__dirname, 'src'), 'node_modules'],
    },
  })
}

module.exports = { onCreateWebpackConfig }
