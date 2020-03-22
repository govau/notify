import React, { createContext } from 'react'
import { StaticQuery, graphql } from 'gatsby'
import MDXRenderer from 'gatsby-mdx/mdx-renderer'

import LanguageSelector, { CurrentLanguage } from './language-selector'
import { PageHeadings } from './table-of-contents'

import * as scope from './examples-components'

const Context = createContext(new Map())

const groupBy = identify => (groups, node) => {
  const identifier = identify(node)
  const current = groups.get(identifier) || []
  return groups.set(identifier, [...current, node])
}

const groupByDirectory = groupBy(node => node.parent.relativeDirectory)

const getSectionPath = (headings, title) => {
  const match = headings.find(heading => heading.title === title)
  return match && match.url
}

export const Provider = ({ source = 'data', ...props }) => (
  <StaticQuery
    query={graphql`
      query {
        allMdx {
          edges {
            node {
              id
              parent {
                ... on File {
                  sourceInstanceName
                  relativeDirectory
                  name
                }
              }
              frontmatter {
                title
                lang
              }
              code {
                body
              }
            }
          }
        }
      }
    `}
    render={data => {
      return (
        <Context.Provider
          {...props}
          value={data.allMdx.edges
            .filter(({ node }) => node.parent.sourceInstanceName === source)
            .map(({ node }) => node)
            .reduce(groupByDirectory, new Map())}
        />
      )
    }}
  />
)

export default ({ reference, title }) => (
  <PageHeadings>
    {headings => (
      <Context.Consumer>
        {examples => (
          <>
            <LanguageSelector
              onChange={language => {
                const path = getSectionPath(headings, title)
                path &&
                  window.history.pushState(null, null, `${path}-${language}`)
              }}
              only={(examples.get(reference) || []).map(
                example => example.frontmatter.lang
              )}
            />
            <CurrentLanguage>
              {language => {
                const ex = (examples.get(reference) || []).find(
                  example => example.frontmatter.lang === language
                )

                if (!ex) {
                  console.warn(
                    `couldnt find example ${reference} for ${language}`
                  )
                  return null
                }

                return <MDXRenderer scope={scope}>{ex.code.body}</MDXRenderer>
              }}
            </CurrentLanguage>
          </>
        )}
      </Context.Consumer>
    )}
  </PageHeadings>
)
