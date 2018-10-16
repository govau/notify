import React from 'react'
import SyntaxHighligher from 'react-syntax-highlighter'
import ReactMarkdown from 'react-markdown'

const customStyle = { margin: 0 }
export default ({ content, language }) => {
  if (language && language.toLowerCase() === 'md') {
    return (
      <ReactMarkdown
        source={content}
        renderers={{
          pre: React.Fragment,
          code: ({ value, language }) => (
            <SyntaxHighligher
              customStyle={customStyle}
              language={language}
              children={value}
            />
          ),
        }}
      />
    )
  }

  return (
    <SyntaxHighligher
      customStyle={customStyle}
      language={language}
      children={content}
    />
  )
}
