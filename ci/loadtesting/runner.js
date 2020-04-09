import crypto from 'k6/crypto'
import encoding from 'k6/encoding'
import {Rate} from 'k6/metrics'
import http from 'k6/http'
import {check, sleep} from 'k6'

const algToHash = {
  HS256: 'sha256',
  HS384: 'sha384',
  HS512: 'sha512',
}

const sign = (data, hashAlg, secret) => {
  let hasher = crypto.createHMAC(hashAlg, secret)
  hasher.update(data)

  // Some manual base64 rawurl encoding as `Hasher.digest(encodingType)`
  // doesn't support that encoding type yet.
  return hasher
    .digest('base64')
    .replace(/\//g, '_')
    .replace(/\+/g, '-')
    .replace(/=/g, '')
}

const encode = (content, secret, algorithm = 'HS256') => {
  const header = encoding.b64encode(
    JSON.stringify({typ: 'JWT', alg: algorithm}),
    'rawurl',
  )

  const payload = encoding.b64encode(JSON.stringify(content), 'rawurl')
  const signature = sign(header + '.' + payload, algToHash[algorithm], secret)
  return [header, payload, signature].join('.')
}

const create_jwt = ({serviceID, apiKey}) =>
  encode(
    {
      iss: serviceID,
      iat: Math.round(Date.now() / 1000),
    },
    apiKey,
  )

const { STG = 'dev' } = __ENV

export let errorRate = new Rate('errors')

export let options = {
  ext: {
    loadimpact: {
      projectID: 3488213,
      name: `notify-${STG}`,
    },
  },
}

export default function() {
  const {
    API_KEY,
    SERVICE_ID,
    LOADTEST_TEMPLATE_ID,
    API_BASE_URL = 'https://rest-api.notify.gov.au',
  } = __ENV

  const options = {
    headers: {
      Authorization:
        'Bearer ' + create_jwt({serviceID: SERVICE_ID, apiKey: API_KEY}),
      'User-Agent': 'NOTIFY-API-NODE-LOADTESTING/0',
      'Content-Type': 'application/json',
    },
  }

  const run_id = __VU * (__ITER + 1)

  check(
    http.post(
      `${API_BASE_URL}/v2/notifications/email`,
      JSON.stringify({
        template_id: LOADTEST_TEMPLATE_ID,
        email_address: 'success@simulator.amazonses.com',
        personalisation: {run_id},
      }),
      options,
    ),
    {
      'status is 201': r => r.status == 201,
    },
  ) || errorRate.add(1)
}
