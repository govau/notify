import styled from 'styled-components'

export default styled.p`
  max-width: 70rem;
  margin-top: 0;

  * + & {
    margin-top: 1em;
  }
`
