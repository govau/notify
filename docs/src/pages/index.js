import React from 'react'

import { External as Link } from '../components/link'
import Layout from '../components/layout'

export default () => {
  return (
    <Layout>
      <h1>Hi people</h1>
      <p>
        Integrate with the Notify API using one of our clients (links open in a
        new tab)
      </p>

      <ul>
        <li>
          <Link
            blank
            href="https://github.com/alphagov/notifications-java-client"
          >
            Java
          </Link>
        </li>
        <li>
          <Link
            blank
            href="https://github.com/alphagov/notifications-python-client"
          >
            Python
          </Link>
        </li>
        <li>
          <Link
            blank
            href="https://github.com/alphagov/notifications-node-client"
          >
            Node.js
          </Link>
        </li>
      </ul>
    </Layout>
  )
}
