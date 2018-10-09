const crypto = require('crypto')

const isSupportedExtension = extension => ['java', 'py', 'sh', 'groovy', 'cs', 'go', 'rb', 'php', 'md'].indexOf(extension) !== -1

exports.onCreateNode = ({ node, actions, loadNodeContent }, pluginOptions) => {
  if (!pluginOptions.name || pluginOptions.name !== node.sourceInstanceName) {
    return
  }

  if (!isSupportedExtension(node.extension)) {
    return
  }

  return loadNodeContent(node).then(content => {
    const { createNode, createParentChildLink } = actions

    const codeNode = {
      id: `${node.id} >>> CodeSamples`,
      parent: node.id,
      extension: node.extension,
      name: node.name,
      content,
      relativePath: node.relativePath,
      internal: {
        contentDigest: crypto.createHash('md5').update(content).digest('hex'),
        type: 'CodeSamples',
      },
    }
    createNode(codeNode)
    createParentChildLink({ parent: node, child: codeNode })
  })
}