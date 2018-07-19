const { ApolloServer, gql } = require('apollo-server')
const grpc = require('grpc')
const notify = grpc.load('../grpc/defs/notify.proto')

const client = new notify.Notify(
  'localhost:50051',
  grpc.credentials.createInsecure()
)

const getUsers = params =>
  new Promise((resolve, reject) =>
    client.getUsers(params, (err, data) => (err ? reject(err) : resolve(data)))
  )

const servicesForUser = params =>
  new Promise((resolve, reject) =>
    client.servicesForUser(
      params,
      (err, data) => (err ? reject(err) : resolve(data))
    )
  )

getUsers({})
  .then(data => {
    console.log('we got the data.', data.users, data.users[1].id)
    return servicesForUser({ user_id: data.users[1].id }).then(sdata => {
      console.log('we got the services.', sdata)
      return sdata
    })
  })
  .catch(err => console.log('we got the error.', { err }))

const typeDefs = gql`
  schema {
    query: Query
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
`

const flatMap = fx => xs => Array.prototype.concat(...xs.map(fx))

// Resolvers define the technique for fetching the types in the
// schema.  We'll retrieve books from the "books" array above.
const resolvers = {
  Query: {
    user(root, { id }, context, info) {
      return new Promise((resolve, reject) =>
        client.getUser(
          { user_id: id },
          (err, data) => (err ? reject(err) : resolve(data))
        )
      )
    },

    users() {
      return new Promise((resolve, reject) =>
        client.getUsers(
          {},
          (err, data) => (err ? reject(err) : resolve(data.users))
        )
      )
    },
  },

  Template: {
    service(template) {
      return new Promise((resolve, reject) =>
        client.getService({ service_id: template.service }, (err, data) => {
          console.log('template-service', { err, data })
          return err ? reject(err) : resolve(data)
        })
      )
    },
  },

  Service: {
    created_by(service) {
      return new Promise((resolve, reject) =>
        client.getUser(
          { user_id: service.created_by },
          (err, data) => (err ? reject(err) : resolve(data))
        )
      )
    },

    users(service) {
      return Promise.all(
        service.users.map(
          user_id =>
            new Promise((resolve, reject) =>
              client.getUser(
                { user_id },
                (err, user) =>
                  err
                    ? reject(err)
                    : resolve({
                        ...user,
                        permissions: (user.permissions[service.id] || {})
                          .permissions,
                      })
              )
            )
        )
      )
    },

    templates(service) {
      return new Promise((resolve, reject) =>
        client.templatesForService(
          { service_id: service.id },
          (err, data) => (err ? reject(err) : resolve(data.templates))
        )
      )
    },
  },

  User: {
    services(user) {
      return new Promise((resolve, reject) =>
        client.servicesForUser(
          { user_id: user.id },
          (err, data) => (err ? reject(err) : resolve(data.services))
        )
      )
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
