import React from 'react'
import styled from 'styled-components'
import { Flex, Box } from '@rebass/grid'
import { height } from 'styled-system'

import { PanelProvider, Wrapper } from './theme'
import dta from '../images/dta-wordmark-white.svg'
import { External } from './link'
import notifyUrl from './core/notify-url'

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
          <External href={i.href}>{i.text}</External>
        </li>
      ))}
    </Ul>
  </Box>
)

const firstColumn = [
  { text: 'Support', href: notifyUrl('/support') },
  { text: 'System status', href: 'https://status.notify.gov.au/' },
  { text: 'Blog', href: 'https://dta.gov.au/blog' },
]

const secondColumn = [
  { text: 'Getting started', href: notifyUrl('/getting-started') },
  { text: 'Features', href: notifyUrl('/features') },
  { text: 'Roadmap', href: notifyUrl('/features/roadmap') },
  { text: 'Security', href: notifyUrl('/features/security') },
  { text: 'Terms of use', href: notifyUrl('/features/terms') },
  { text: 'Using Notify', href: notifyUrl('/features/using-notify') },
]

const thirdColumn = [
  { text: 'Pricing', href: notifyUrl('/pricing') },
  { text: 'Privacy', href: notifyUrl('/privacy') },
  { text: 'Cookies', href: notifyUrl('/cookies') },
  { text: 'Documentation', href: '/' },
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
