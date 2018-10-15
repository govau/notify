import React from 'react'
import styled from 'styled-components'
import { Flex, Box } from '@rebass/grid'
import { height, space } from 'styled-system'

import { PanelProvider, Wrapper } from './theme'
import dta from '../images/dta-wordmark-white.svg'
import { External } from './link'

const Logo = styled.img`
  padding-left: 0;
  margin-bottom: 2rem;
  ${height};
`

const Root = styled.footer`
  background: ${props => props.theme.background};
  color: ${props => props.theme.content};
  padding-top: 2rem;
  padding-bottom: 5rem;
`

const StyledFlex = styled(Flex)`
  flex-wrap: wrap;
  margin: 4rem 0;

  justify-content: space-between;
  align-items: start;
  border-bottom: 1px solid #bfc1c3;
  padding-bottom: 4rem;

  ${space};
`

const Ul = styled.ul`
  padding-left: 0;
  margin-top: 0;
  margin-bottom: 0;
  list-style-type: none;
`

const UnorderedList = ({ list }) => (
  <Box width={[1, 1 / 4]}>
    <Ul>
      {list.map(i => (
        <li key={i.text}>
          <External blank href={i.target}>
            {i.text}
          </External>
        </li>
      ))}
    </Ul>
  </Box>
)

const firstColumn = [
  { text: 'Support', target: 'https://notify.gov.au/support' },
  { text: 'System status', target: 'https://status.notify.gov.au/' },
  { text: 'Slack channel', target: 'https://ausdta.slack.com/messages/notify' },
  { text: 'Blog', target: 'https://dta.gov.au/blog' },
]

const secondColumn = [
  { text: 'Features', target: 'https://notify.gov.au/features' },
  { text: 'Roadmap', target: 'https://notify.gov.au/features/roadmap' },
  { text: 'Security', target: 'https://notify.gov.au/features/security' },
  { text: 'Terms of use', target: 'https://notify.gov.au/features/terms' },
  {
    text: 'Using Notify',
    target: 'https://notify.gov.au/features/using-notify',
  },
]

const thirdColumn = [
  { text: 'Pricing', target: 'https://notify.gov.au/pricing' },
  { text: 'Cookies', target: 'https://notify.gov.au/cookies' },
  { text: 'Documentation', target: 'https://notify.gov.au/documentation' },
]

export default props => (
  <PanelProvider>
    <Root>
      <Wrapper>
        <StyledFlex pr={[0, '10rem']}>
          <Box width={[1, 1 / 4]}>
            <Logo src={dta} height={['4rem', '4rem', '6rem']} />
          </Box>
          <UnorderedList list={firstColumn} />
          <UnorderedList list={secondColumn} />
          <UnorderedList list={thirdColumn} />
        </StyledFlex>
      </Wrapper>

      <Wrapper>
        © Commonwealth of Australia. With the exception of the Commonwealth Coat
        of Arms and where otherwise noted, this work is licensed under the{' '}
        <External
          blank
          href="https://github.com/govau/notify/blob/master/admin/LICENSE"
        >
          MIT license
        </External>
        .
      </Wrapper>
    </Root>
  </PanelProvider>
)
