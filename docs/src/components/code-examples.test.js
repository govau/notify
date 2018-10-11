import React from 'react'
import renderer from 'react-test-renderer'
import { filterTransformSortCodeSnippets } from './code-examples'
import mockGraphQLResponse from './code-examples.test.fixture'

const mockData = mockGraphQLResponse.allCodeSamples.edges

test.each`
  data         | path                | expectedLength | testDescription
  ${mockData}  | ${'sending-emails'} | ${3}           | ${'filters correctly'}
  ${mockData}  | ${'unknown-path'}   | ${0}           | ${'returns empty array no matches found'}
  ${[]}        | ${'sending-emails'} | ${0}           | ${'returns empty array when data is empty'}
  ${null}      | ${'sending-emails'} | ${0}           | ${'returns empty array when data is null'}
  ${undefined} | ${'sending-emails'} | ${0}           | ${'returns empty array when data is undefined'}
`(
  'filterTransformSortCodeSnippets $testDescription',
  ({ data, path, expectedLength }) => {
    expect(
      filterTransformSortCodeSnippets({
        codeSnippets: mockGraphQLResponse.allCodeSamples.edges,
        path: 'sending-emails',
      })
    ).toHaveLength(3)
  }
)
