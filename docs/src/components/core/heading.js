import styled, { css } from 'styled-components'

import P from './paragraph'

export const H1 = styled.h1`
  ${props => (props.appearAs ? props.appearAs.__styles : H1.__styles)};

  &
    + ${P},
    &
    + ${P}
    + ${P},
    &
    + ${P}
    + ${P}
    + ${P},
    &
    + ${P}
    + ${P}
    + ${P}
    + ${P},
    &
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P},
    &
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P},
    &
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P},
    &
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P}
    + ${P} {
    font-size: 1.25em;
    font-weight: 300;
  }
`

export const H2 = styled.h2`
  ${props => (props.appearAs ? props.appearAs.__styles : H2.__styles)};

  &:target {
    background-color: #fec0ff;
  }
`

export const H3 = styled.h3`
  ${props => (props.appearAs ? props.appearAs.__styles : H3.__styles)};
`

export const H4 = styled.h4`
  ${props => (props.appearAs ? props.appearAs.__styles : H4.__styles)};
`

H1.__styles = css`
  font-size: 3em;
`

H2.__styles = css`
  font-size: 2em;
`

H3.__styles = css`
  font-size: 1.5em;
`

H4.__styles = css`
  font-size: 1.25em;
`
