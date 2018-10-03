import React from 'react'

export default ({ children, ...props }) => (
  <button {...props}>{children}</button>
)
