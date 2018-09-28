import React from 'react'
import { MDXProvider } from '@mdx-js/tag'
import ThemeProvider from './theme'

import Code from './code'

export default ({ children }) => (
  <ThemeProvider>
    <MDXProvider
      components={{
        code: ({ children }) => {
          return <Code language="ocaml">{children}</Code>
        },
      }}
    >
      {children}
    </MDXProvider>
  </ThemeProvider>
)
