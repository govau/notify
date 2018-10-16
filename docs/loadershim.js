global.___loader = {
  enqueue: jest.fn(),
}

const gatsby = jest.requireActual('gatsby')
module.exports = { ...gatsby, graphql: jest.fn() }
