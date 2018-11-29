import React from 'react'
import { MDXProvider } from '@mdx-js/tag'

import ThemeProvider from './theme'
import P from './core/paragraph'
import { H3, H4, AnchoredH1, AnchoredH2 } from './core/heading'
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

// https://github.com/mdx-js/mdx/blob/e6a7b03fc7df49de4e05b6ff1bf4d7b693ff39b7/packages/mdx/test/index.test.js#L84
const getMetadata = ({ className, ...metadata }) => metadata

export default ({ children }) => (
  <ThemeProvider>
    <ExampleProvider>
      <LanguageProvider>
        <MDXProvider
          components={{
            wrapper: React.Fragment,
            pre: React.Fragment,
            code: ({ children, ...props }) => (
              <SyntaxHighlighter
                language={getLanguage(props)}
                metadata={getMetadata(props)}
                content={children}
              />
            ),
            p: P,
            h1: AnchoredH1,
            h2: AnchoredH2,
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
