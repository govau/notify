import React from 'react'
import styled from 'styled-components'
import { util } from 'styled-system'
import { Flex } from '@rebass/grid'

import MenuIcon from './icons/menu-icon'
import CloseIcon from './icons/close-icon'
import coa from '../images/coa_white.svg'
import { Wrapper, PanelProvider } from './theme'
import { External } from './link'
import notifyUrl from './core/notify-url'

const Root = styled.header`
  background: ${props => props.theme.background};
  color: ${props => props.theme.content};
  border-bottom: 0.5rem solid #45c2f0;
`

const BannerLink = styled.a`
  text-decoration: none;
  color: #fff;

  &:hover {
    cursor: pointer;
  }
`

const Logo = styled.img`
  display: none;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    display: initial;
    border-right: 1px solid #a9a9a9;
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

const OpenMenuLink = styled.a`
  color: #fff;
  align-self: center;
  text-decoration: none;
  display: flex;
  align-items: center;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    display: none;
  }
`

const MenuText = styled.span`
  margin-right: 0.7rem;
  font-size: 1.7rem;
`

const CloseLink = styled.a`
  display: block;
  color: #fff;
  text-align: center;
  margin-bottom: 2.5rem;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    display: none;
  }
`

const StyledUnsortedList = styled.ul`
  list-style: none;
  margin: 0 0 0 -1.5rem;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
`

const ListItem = styled.li`
  padding-right: 1.5rem;
  padding-bottom: 1rem;
  padding-left: 1.5rem;
  width: 100%;

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    width: auto;
    margin-bottom: -0.5rem;
    padding-bottom: 1.5rem;
    border-bottom: ${props =>
      props.active ? '0.5rem solid #fff' : '0.5rem solid #45c2f0'};

    &:last-child {
      margin-left: auto;
    }
  }
`

const ExternalLink = styled(External)`
  text-decoration: none;
  color: ${props => (props.active ? '#45c2f0' : '#fff')};

  ${util.createMediaQuery(util.defaultBreakpoints[0])} {
    color: white;
  }
`

export default () => (
  <PanelProvider>
    <Root>
      <Wrapper>
        <Flex justifyContent="space-between">
          <BannerLink href={notifyUrl('')}>
            <Flex
              justifyContent="flex-start"
              p={['1rem 0', '3rem 0']}
              alignItems="center"
            >
              <Logo src={coa} />
              <HeaderName>Notify</HeaderName>
              <Badge>Alpha</Badge>
            </Flex>
          </BannerLink>
          <OpenMenuLink href="#nav" aria-label="Open navigation">
            <MenuText>Menu</MenuText>
            <MenuIcon />
          </OpenMenuLink>
        </Flex>

        <Nav id="nav">
          <CloseLink href="#" aria-label="Close navigation">
            <CloseIcon />
          </CloseLink>
          <StyledUnsortedList>
            <ListItem>
              <ExternalLink href={notifyUrl('support')}>Support</ExternalLink>
            </ListItem>
            <ListItem>
              <ExternalLink href={notifyUrl('features')}>Features</ExternalLink>
            </ListItem>
            <ListItem>
              <ExternalLink href={notifyUrl('pricing')}>Pricing</ExternalLink>
            </ListItem>
            <ListItem active>
              <ExternalLink active href="/">
                Documentation
              </ExternalLink>
            </ListItem>
            <ListItem>
              <ExternalLink href={notifyUrl('sign-in')}>Sign in</ExternalLink>
            </ListItem>
          </StyledUnsortedList>
        </Nav>
      </Wrapper>
    </Root>
  </PanelProvider>
)
