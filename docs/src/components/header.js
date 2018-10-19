import React from 'react'
import styled from 'styled-components'
import { util } from 'styled-system'
import { Flex, Box } from '@rebass/grid'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

import dta from '../images/coa_white.svg'
import { Wrapper, PanelProvider } from './theme'
import { External } from './link'

const notifyBaseUrl = process.env.GATSBY_NOTIFY_BASE_URL
  ? process.env.GATSBY_NOTIFY_BASE_URL
  : 'https://notify.gov.au'

const Root = styled.header`
  background: ${props => props.theme.background};
  color: ${props => props.theme.content};
  border-bottom: 0.5rem solid #45c2f0;
`

const BannerLink = styled.a`
  text-decoration: none;

  & :hover {
    cursor: pointer;
  }
`

const Logo = styled.img`
  border-right: 1px solid #a9a9a9;
  height: 6rem;
  padding: 0.25rem 0.5rem;
  margin-left: -1rem;
  margin-right: 1rem;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    height: 8rem;
    padding: 0.25rem 2.5rem 0.25rem 0;
    margin-left: -0.5rem;
    margin-right: 2.5rem;
  }
`

const HeaderName = styled.span`
  font-weight: bold;
  white-space: nowrap;
  font-size: 2.5rem;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    font-size: 3rem;
  }
`

const Badge = styled.span`
  padding: 1px 8px;
  margin-left: 0.5rem;
  border: solid 2px #fff;
  border-radius: 2em;
  font-weight: bold;
  vertical-align: super;
  white-space: nowrap;
  font-size: 1rem;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    font-size: 1.5rem;
  }
`

const Nav = styled.nav`
  padding: 20px;
  position: fixed;
  height: 100%;
  top: 0;
  width: 100%;
  background: #313131;
  z-index: 5;
  text-align: center;

  &:not(:target) {
    right: -100%;
    transition: right 0.5s;
  }

  &:target {
    right: 0;
    transition: right 0.5s;
  }

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    padding: initial;
    position: initial;
    height: initial;
    top: initial;
    width: initial;
    background: initial;

    &:not(:target) {
      right: initial;
      transition: initial;
    }

    &:target {
      right: initial;
      transition: initial;
    }
  }
`

const HamburgerIcon = styled.a`
  color: #fff;
  align-self: flex-end;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    display: none;
  }
`

const CloseIcon = styled.a`
  display: block;
  color: #fff;
  text-align: center;
  margin-bottom: 1rem;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    display: none;
  }
`

const Navitems = styled.ul`
  list-style: none;
  margin: 0;
  padding: 0;
`

const Navitem = styled.li`
  display: inline;
  padding-right: 1.5rem;
  padding-bottom: 1rem;
  padding-left: 1.5rem;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    padding-bottom: 1.5rem;
    border-bottom: ${props =>
      props.active ? '0.5rem solid #fff' : '0.5rem solid #45c2f0'};

    & :last-child {
      margin-left: auto;
    }
  }
`

const StyledExternalLink = styled(External)`
  text-decoration: none;
  color: ${props => (props.active ? '#45c2f0' : '#fff')};

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    color: white;
  }
`

const MyNavItem = ({ children, href, active, ...props }) => (
  <Box mb={['0.7rem', '0.1rem']} width={[1, 'auto']} {...props}>
    <Navitem active={active}>
      <StyledExternalLink href={href} active={active}>
        {children}
      </StyledExternalLink>
    </Navitem>
  </Box>
)

export default () => (
  <PanelProvider>
    <Root>
      <Wrapper>
        <Flex justifyContent="space-between">
          <BannerLink to="/">
            <Flex justifyContent="flex-start" p={'3rem 0'} alignItems="center">
              <Logo src={dta} />
              <HeaderName>Notify</HeaderName>
              <Badge>Alpha</Badge>
            </Flex>
          </BannerLink>
          <HamburgerIcon href="#nav" aria-label="Open Navigation">
            <FontAwesomeIcon icon="bars" />
          </HamburgerIcon>
        </Flex>

        <Nav id="nav">
          <CloseIcon href="#" aria-label="Close Navigation">
            <FontAwesomeIcon icon="times" className="fa-lg" />
          </CloseIcon>
          <Navitems>
            <Flex flexWrap="wrap" m={[0, '1rem 0 1rem -1.5rem']}>
              <Box width={[1, 'auto']}>
                <Flex flexWrap="wrap">
                  <MyNavItem href={`${notifyBaseUrl}/support`}>
                    Support
                  </MyNavItem>
                  <MyNavItem href={`${notifyBaseUrl}/features`}>
                    Features
                  </MyNavItem>
                  <MyNavItem href={`${notifyBaseUrl}/pricing`}>
                    Pricing
                  </MyNavItem>
                  <MyNavItem active href="/">
                    Documentation
                  </MyNavItem>
                </Flex>
              </Box>

              <MyNavItem
                ml={[0, 'auto']}
                mr={[0, '5rem']}
                href={`${notifyBaseUrl}/sign-in`}
              >
                Sign in
              </MyNavItem>
            </Flex>
          </Navitems>
        </Nav>
      </Wrapper>
    </Root>
  </PanelProvider>
)
