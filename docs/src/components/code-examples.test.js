import React from 'react'
import renderer from 'react-test-renderer'
import { CodeExamplesComponent } from './code-examples'
import mockQuery from './code-examples.test.fixture'

describe('CodeExamplesComponent', () =>
  it('renders correctly', () => {
    const tree = renderer
      .create(<CodeExamplesComponent data={mockQuery} path="sending-emails" />)
      .toJSON()
    expect(tree).toMatchSnapshot()
  }))
