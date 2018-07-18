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

getUsers({ user_id: 'a user. here it is' })
  .then(data => console.log('we got the data.', data.users))
  .catch(err => console.log('we got the error.', { err }))
