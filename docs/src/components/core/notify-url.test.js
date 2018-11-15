import notifyUrl, { stripTrailingSlash } from './notify-url'

test.each`
  input        | expected
  ${'one'}     | ${'one'}
  ${'one/'}    | ${'one'}
  ${'one////'} | ${'one'}
  ${'/one/'}   | ${'/one'}
  ${'/one///'} | ${'/one'}
  ${'/one'}    | ${'/one'}
`(
  'stripTrailingSlash should return $expected from $input',
  ({ input, expected }) => {
    expect(stripTrailingSlash(input)).toEqual(expected)
  }
)

test.each`
  input            | expected
  ${'/path'}       | ${'https://notify.gov.au/path'}
  ${'////path'}    | ${'https://notify.gov.au/path'}
  ${'/one/two'}    | ${'https://notify.gov.au/one/two'}
  ${'///one/two'}  | ${'https://notify.gov.au/one/two'}
  ${'///one//two'} | ${'https://notify.gov.au/one//two'}
  ${'one'}         | ${'https://notify.gov.au/one'}
  ${'one/two'}     | ${'https://notify.gov.au/one/two'}
  ${'one//two'}    | ${'https://notify.gov.au/one//two'}
  ${''}            | ${'https://notify.gov.au/'}
  ${'/'}           | ${'https://notify.gov.au/'}
`(
  'stripLeadingSlash should return $expected from $input',
  ({ input, expected }) => {
    expect(notifyUrl(input)).toEqual(expected)
  }
)
