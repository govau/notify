import React from 'react'
import { MDXProvider } from '@mdx-js/tag'
import ThemeProvider from './theme'

import Code from './code'

export default ({ children }) => (
  <ThemeProvider>
    <MDXProvider
      components={{
        pre: React.Fragment,
        code: ({ children, ...props }) => (
          <Code language={props.lang}>{children}</Code>
        ),
      }}
    >
      {children}
    </MDXProvider>
  </ThemeProvider>
)
