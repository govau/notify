import React from 'react'
import styled, { css } from 'styled-components'
import SyntaxHighligher from 'react-syntax-highlighter'
import { StaticQuery, graphql } from 'gatsby'
import ReactMarkdown from 'react-markdown'

const linkCSS = css`
  line-height: 1.25;
  padding: 1.25rem 1.5rem;
  border-bottom: ${props =>
    props.active ? '0.35rem solid #007099' : '0.35rem solid #e0e0e0'};
  text-decoration: none;
  display: block;
  color: #007099;

  &:hover {
    color: #000;
    cursor: pointer;
  }
`

const Tabs = styled.div`
  margin-top: 1rem;
  border-top: 1px solid #cfcfcf;
`

const TabsNav = styled.div`
  border-bottom: 0.35rem solid #e0e0e0;
  width: 100%;
`

const Ul = styled.ul`
  margin: 0 0 -0.35rem;
  padding: 0;
  display: inline-block;
  line-height: 1.5;
  list-style-type: none;
`

const NavItem = styled.li`
  margin: 0;
  padding: 0;
  display: inline-block;
`

const NavLink = styled.label`
  ${linkCSS};
`

const TabContent = styled.div`
  display: ${props => (props.active ? 'visible' : 'none')};
`

export default class CodeExamples extends React.Component {
  state = {
    activeTab: 0,
  }

  handleClick = index => {
    this.setState({ activeTab: index })
  }

  filterTransformSortCodeSnippets = codeSnippets =>
    codeSnippets
      .filter(n => n.node.relativePath.startsWith(this.props.path))
      .map(n => n.node)
      .sort((a, b) => a.name.localeCompare(b.name))

  syntaxHighlighter = snippet => {
    const customStyle = { margin: 0 }
    if (snippet.extension && snippet.extension.toLowerCase() === 'md') {
      return (
        <ReactMarkdown
          source={snippet.content}
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
        language={snippet.extension}
        children={snippet.content}
      />
    )
  }

  renderTabs = data => {
    const codeSnippets = this.filterTransformSortCodeSnippets(
      data.allCodeSamples.edges
    )
    return (
      <Tabs>
        <TabsNav>
          <Ul>
            {codeSnippets.map((s, i) => (
              <NavItem key={i}>
                <NavLink
                  onClick={() => this.handleClick(i)}
                  active={this.state.activeTab === i}
                >
                  {s.name}
                </NavLink>
              </NavItem>
            ))}
          </Ul>
        </TabsNav>

        {codeSnippets.map((s, i) => (
          <TabContent key={i} active={this.state.activeTab === i}>
            {this.syntaxHighlighter(s)}
          </TabContent>
        ))}
      </Tabs>
    )
  }

  render = () => (
    <StaticQuery
      query={graphql`
        query {
          allCodeSamples {
            edges {
              node {
                content
                extension
                relativePath
                name
              }
            }
          }
        }
      `}
      render={data => this.renderTabs(data)}
    />
  )
}
