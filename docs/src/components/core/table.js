import styled from 'styled-components'

export const Table = styled.table`
  width: 100%;

  & tbody tr {
    border-top: 1px solid #bfc1c3;
  }

  & tbody tr:first-of-type {
    border-top: none;
  }

  & tbody tr td {
    padding: 0.8rem 4rem 0.8rem 0;
  }
`
