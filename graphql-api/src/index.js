const { ApolloServer, gql } = require('apollo-server')
const grpc = require('grpc')
const notify = grpc.load('../proto/notify.proto')

const client = new notify.Notify(
  'localhost:50051',
  grpc.credentials.createInsecure()
)

const promisify = rpc => (
  params,
  resolver = data => data,
  rejecter = err => {
    console.warn(err.details)
    return err
  }
) =>
  new Promise((resolve, reject) =>
    rpc(
      params,
      (err, data) => (err ? reject(rejecter(err)) : resolve(resolver(data)))
    )
  )

const getUser = promisify(client.getUser.bind(client))
const getUsers = promisify(client.getUsers.bind(client))
const getService = promisify(client.getService.bind(client))
const createTemplate = promisify(client.createTemplate.bind(client))
const templatesForService = promisify(client.templatesForService.bind(client))
const servicesForUser = promisify(client.servicesForUser.bind(client))

const typeDefs = gql`
  schema {
    query: Query
    mutation: Mutation
  }

  type Permission {
    service: String
    permission: String
  }

  type Template {
    id: String
    name: String
    subject: String
    content: String
    template_type: String
    created_at: String
    created_by: String
    process_type: String
    archived: Boolean
    service: Service
  }

  type Service {
    active: Boolean
    branding: String
    email_from: String
    id: String
    name: String
    organisation_type: String
    rate_limit: Int
    annual_billing: [String!]
    permissions: [String!]
    user_to_service: [String!]
    templates: [Template!]

    users: [ServiceUser!]
    created_by: User
  }

  type User {
    id: String
    name: String
    auth_type: String
    email_address: String
    failed_login_count: Int
    password_changed_at: String
    permissions: [Permission!]
    services: [Service!]
  }

  type ServiceUser {
    id: String
    name: String
    auth_type: String
    email_address: String
    failed_login_count: Int
    password_changed_at: String
    permissions: [String!]
  }

  type Query {
    user(id: String!): User
    users: [User!]
  }

  type Mutation {
    createTemplate(
      service_id: String!
      created_by: String!
      name: String!
      subject: String!
      content: String!
    ): Template
  }
`

const flatMap = fx => xs => Array.prototype.concat(...xs.map(fx))

// Resolvers define the technique for fetching the types in the
// schema.  We'll retrieve books from the "books" array above.
const resolvers = {
  Query: {
    user(root, { id }, context, info) {
      return getUser({ user_id: id })
    },

    users() {
      return getUsers({}, data => data.users)
    },
  },

  Mutation: {
    createTemplate(root, params, context, info) {
      return createTemplate(params)
    },
  },

  Template: {
    service(template) {
      return getService({ service_id: template.service })
    },
  },

  Service: {
    created_by(service) {
      return getUser({ user_id: service.created_by })
    },

    users(service) {
      return Promise.all(
        service.users.map(user_id =>
          getUser({ user_id }, user => ({
            ...user,
            permissions: (user.permissions[service.id] || {}).permissions,
          }))
        )
      )
    },

    templates(service) {
      return templatesForService(
        { service_id: service.id },
        data => data.templates
      )
    },
  },

  User: {
    services(user) {
      return servicesForUser({ user_id: user.id }, data => data.services)
    },

    permissions(user) {
      return flatMap(({ service, permissions }) =>
        permissions.map(permission => ({ service, permission }))
      )(
        Object.entries(user.permissions).map(([service, permissions]) => ({
          service,
          permissions: permissions.permissions,
        }))
      )
    },
  },
}

// In the most basic sense, the ApolloServer can be started
// by passing type definitions (schema) and the resolvers
// responsible for fetching the data for those types.
const server = new ApolloServer({ typeDefs, resolvers })

// This `listen` method launches a web-server.  Existing apps
// can utilize middleware options, which we'll discuss later.
server.listen().then(({ url }) => {
  console.log(`🚀  Server ready at ${url}`)
})
