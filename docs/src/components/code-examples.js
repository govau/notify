import React from 'react'
import Code from './code'

export default props => (
  <div>
    <div>code examples for {props.subject}</div>
    <Code language="python">lambda x: x + 1</Code>
  </div>
)
