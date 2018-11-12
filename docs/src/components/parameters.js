import React, { Fragment } from 'react'
import styled from 'styled-components'

import { nondesktop, desktop } from './core/media'

const Requirements = styled.section``

const Requirement = styled.span`
  border-radius: 3px;
  padding: 4px 8px;
  font-size: 0.8em;
`

const Required = styled(Requirement)`
  background-color: #ddefbc;
  color: #466709;
`

const Optional = styled(Requirement)`
  background-color: #bcd9ef;
  color: #074371;
`

const Description = styled.dd`
  margin: 0;

  @media ${desktop} {
    grid-column-start: 2;
  }
`

const Term = styled.dt`
  @media ${desktop} {
    grid-column-start: 1;
  }

  @media ${nondesktop} {
    display: flex;
    justify-content: space-between;

    ${Description} + & {
      margin-top: 2em;
      padding-top: 1em;
      border-top: 1px solid #eee;
    }

    & + ${Description} {
      margin-top: 1em;
    }
  }
`

const Parameters = styled.dl`
  @media ${desktop} {
    display: grid;
    grid-template-columns: max-content auto;
    grid-row-gap: 1em;
    grid-column-gap: 2em;
  }
`

const Code = styled.code`
  @media ${nondesktop} {
    background-color: #f1f1f1;
    border-radius: 3px;
    padding: 2px 4px;
  }
`

const Parameter = ({ required = false, optional = false, name, children }) => (
  <Fragment>
    <Term>
      <Code>{name}</Code>
      <Requirements>
        {required ? (
          <Required>Required</Required>
        ) : optional ? (
          <Optional>Optional</Optional>
        ) : null}
      </Requirements>
    </Term>
    <Description>{children}</Description>
  </Fragment>
)

export { Parameter as default, Parameter, Parameters }
