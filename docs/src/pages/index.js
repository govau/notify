import React from 'react'

import Link from '../components/link'
import Layout from '../components/layout'
import { H1 } from '../components/core/heading'
import P from '../components/core/paragraph'

export default () => {
  return (
    <Layout>
      <H1>Using Notify</H1>
      <P>
        Notify is a service developed by the DTA that lets government agencies
        to send and receive text messages and email messages.
      </P>

      <div className="prevent-next-paragraphs-from-getting-hero-text" />

      <P>
        You can start using Notify right away without a technical team. The user
        interface allows you to manage templates and send out messages manually.
      </P>

      <P>
        Notify also allows you to send out messages automatically by integrating
        with an API. You might do this if you have a system that tracks a
        business process.
      </P>
      <P>
        <Link to="/installation">Get started</Link>
      </P>
    </Layout>
  )
}
