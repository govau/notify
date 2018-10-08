import styled from 'styled-components'

import P from './paragraph'

export const H1 = styled.h1`
  font-size: 3em;

  &,
  & + ${P}, & + ${P} + ${P} {
    color: ${props => props.theme.subtle};
  }

  & + ${P}, & + ${P} + ${P} {
    font-size: 1.4em;
    font-weight: 300;
  }
`

export const H2 = styled.h2`
  font-size: 2.2em;
`

export const H3 = styled.h3`
  font-size: 1.7em;
`

export const H4 = styled.h4``
