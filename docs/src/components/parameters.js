import React, { Fragment } from 'react'
import styled from 'styled-components'

import { nondesktop, desktop } from './core/media'

const Requirements = styled.section``

const Requirement = styled.span`
  border-radius: 3px;
  padding: 4px 8px;
  font-size: 0.8em;
`

const RequirementKind = styled.span`
  font-weight: 500;
  background-color: rgba(255, 255, 255, 0.5);
  padding: 1px 4px;
`

const Required = styled(Requirement)`
  background-color: #ddefbc;
  color: #466709;
`

const Optional = styled(Requirement)`
  background-color: #bcd9ef;
  color: #074371;
`

const NoRequirement = styled(Requirement)`
  background-color: #d8d8d8;
  color: #5d5d5d;

  ${RequirementKind} {
    background: none;
  }
`

const Description = styled.dd`
  margin: 0;

  @media ${desktop} {
    grid-column-start: 2;

    /*
    * prevents this cell from overflowing the css grid because code examples
    * stretch everything out.
    *
    * https://stackoverflow.com/questions/43311943/prevent-content-from-expanding-grid-items
    */
    overflow: hidden;
    min-width: 0;
  }
`

const Term = styled.dt`
  @media ${desktop} {
    grid-column-start: 1;
  }

  @media ${nondesktop} {
    display: flex;
    flex-flow: row wrap;
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

    /* prevent cell from overflowing. see 'Description' */
    min-height: 0;
    min-width: 0;
  }
`

const Code = styled.code`
  @media ${nondesktop} {
    background-color: #f1f1f1;
    border-radius: 3px;
    padding: 2px 4px;
  }
`

const Kind = ({ children }) =>
  children ? (
    <Fragment>
      {' '}
      <RequirementKind>{children}</RequirementKind>
    </Fragment>
  ) : null

const Parameter = ({
  required = false,
  optional = false,
  kind,
  name,
  children,
}) => (
  <Fragment>
    <Term>
      <Code>{name}</Code>
      <Requirements>
        {required ? (
          <Required>
            Required
            <Kind>{kind}</Kind>
          </Required>
        ) : optional ? (
          <Optional>
            Optional
            <Kind>{kind}</Kind>
          </Optional>
        ) : kind ? (
          <NoRequirement>
            <Kind>{kind}</Kind>
          </NoRequirement>
        ) : null}
      </Requirements>
    </Term>
    <Description>{children}</Description>
  </Fragment>
)

export { Parameter as default, Parameter, Parameters }
