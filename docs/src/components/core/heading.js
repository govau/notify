import React, { Fragment } from 'react'
import styled, { css } from 'styled-components'

import P from './paragraph'

const InitiallyHiddenLink = styled.a`
  color: ${props => props.theme.content};
  text-decoration: none;
  opacity: 0;

  &:focus {
    opacity: 1;
  }
`

// TODO: use an icon library for this link?
const Permalink = ({ id }) =>
  id ? (
    <Fragment>
      {' '}
      <InitiallyHiddenLink href={`#${id}`}>
        <span role="img" aria-label="permalink">
          ¶
        </span>
      </InitiallyHiddenLink>
    </Fragment>
  ) : null

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
`

export const H3 = styled.h3`
  ${props => (props.appearAs ? props.appearAs.__styles : H3.__styles)};
`

export const H4 = styled.h4`
  ${props => (props.appearAs ? props.appearAs.__styles : H4.__styles)};
`

const AnchoredHeading = Heading => styled(({ children, ...props }) => (
  <Heading {...props}>
    {children}
    <Permalink id={props.id} />
  </Heading>
))`
  &:hover ${InitiallyHiddenLink}, &:target ${InitiallyHiddenLink} {
    opacity: 1;
  }
`

export const AnchoredH1 = AnchoredHeading(H1)

export const AnchoredH2 = AnchoredHeading(H2)

// Content below a heading should be visually closer to it so that it is
// associated with that heading.
//
// Content above a heading should be spaced further away so it does not
// associate with the heading.
const common = css`
  margin-top: 1rem;
  margin-bottom: 1rem;

  * + & {
    margin-top: 1em;
    margin-bottom: 1rem;
  }
`

H1.__styles = css`
  ${common};
  font-size: 3em;
`

H2.__styles = css`
  ${common};
  font-size: 2em;
`

H3.__styles = css`
  ${common};
  font-size: 1.5em;
`

H4.__styles = css`
  ${common};
  font-size: 1.25em;
`
