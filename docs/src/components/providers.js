import React from 'react'
import { MDXProvider } from '@mdx-js/tag'
import ThemeProvider from './theme'

import Code from './code'
import P from './core/paragraph'
import { H1, H2, H3, H4 } from './core/heading'

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
        p: P,
        h1: H1,
        h2: H2,
        h3: H3,
        h4: H4,
      }}
    >
      {children}
    </MDXProvider>
  </ThemeProvider>
)
