import React from 'react'
import SyntaxHighligher from 'react-syntax-highlighter'
import ReactMarkdown from 'react-markdown'
import { ascetic } from 'react-syntax-highlighter/dist/styles/hljs'

const customStyle = { margin: 0, padding: '2rem' }

const inlineStyle = { margin: 0, padding: 0 }

const lineNumberContainerStyle = {
  paddingRight: '1.5em',
  float: 'left',
}

export default ({
  content,
  language,
  metadata: { inline = false, nonumbers: noNumbers = false } = {},
}) => {
  if (language && language.toLowerCase() === 'md') {
    return (
      <ReactMarkdown
        source={content}
        renderers={{
          pre: React.Fragment,
          code: ({ value, language }) => (
            <SyntaxHighligher
              style={ascetic}
              customStyle={inline ? inlineStyle : customStyle}
              language={language}
              children={value}
              showLineNumbers={!noNumbers}
              lineNumberContainerStyle={lineNumberContainerStyle}
            />
          ),
        }}
      />
    )
  }

  return (
    <SyntaxHighligher
      style={ascetic}
      customStyle={inline ? inlineStyle : customStyle}
      language={language}
      children={content}
      showLineNumbers={!noNumbers}
      lineNumberContainerStyle={lineNumberContainerStyle}
    />
  )
}
