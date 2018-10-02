import React from 'react'
import { MDXProvider } from '@mdx-js/tag'
import ThemeProvider from './theme'

import Code from './code'

const getLanguage = props => {
  const re = /language-(\w+)/g
  const matches = re.exec(props.className)

  return props.lang ? props.lang : matches ? matches[1] : undefined
}

export default ({ children }) => (
  <ThemeProvider>
    <MDXProvider
      components={{
        pre: React.Fragment,
        code: ({ children, ...props }) => (
          <Code language={getLanguage(props)}>{children}</Code>
        ),
      }}
    >
      {children}
    </MDXProvider>
  </ThemeProvider>
)
