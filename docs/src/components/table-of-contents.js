import React, { createContext } from 'react'
import styled from 'styled-components'

import Link from './link'
import { H2, H4 } from './core/heading'

const Contents = styled.section`
  padding-left: 1.5rem;
  border-left: 2px solid ${props => props.theme.content};

  & ${H2} {
    margin-bottom: 0;
    margin-top: 0;
  }
`

const Ul = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  line-height: 1.9em;
`

export const { Provider, Consumer } = createContext([])

export default ({ title = 'Contents', children }) => (
  <Contents>
    <H2 appearAs={H4}>{title}</H2>
    <Ul>
      {children || (
        <Consumer>
          {headings =>
            headings
              ? headings.map((heading, i) => (
                  <li key={i}>
                    <Link to={heading.url}>{heading.title}</Link>
                  </li>
                ))
              : null
          }
        </Consumer>
      )}
    </Ul>
  </Contents>
)
