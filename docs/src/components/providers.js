import React from 'react'
import { MDXProvider } from '@mdx-js/tag'

import ThemeProvider from './theme'
import P from './core/paragraph'
import { H1, H2, H3, H4 } from './core/heading'
import { Table } from './core/table'
import SyntaxHighlighter from './syntax-highlighter'
import { BlockQuote } from './core/blockquote'
import { Provider as LanguageProvider } from './language-selector'
import { Provider as ExampleProvider } from './examples'

const getLanguage = props => {
  const re = /language-(\w+)/g
  const matches = re.exec(props.className)

  return props.lang ? props.lang : matches ? matches[1] : undefined
}

export default ({ children }) => (
  <ThemeProvider>
    <ExampleProvider>
      <LanguageProvider>
        <MDXProvider
          components={{
            pre: React.Fragment,
            code: ({ children, ...props }) => (
              <SyntaxHighlighter
                language={getLanguage(props)}
                content={children}
              />
            ),
            p: P,
            h1: H1,
            h2: H2,
            h3: H3,
            h4: H4,
            table: Table,
            blockquote: BlockQuote,
          }}
        >
          {children}
        </MDXProvider>
      </LanguageProvider>
    </ExampleProvider>
  </ThemeProvider>
)
