import { languages } from '../config'
import { getGlobals } from './globals'

export function getLangInHash() {
  return getGlobals(({ win }) => {
    const winHash = win.location.hash
    return Object.keys(languages).find(lang => {
      const re = new RegExp(`-${lang}$`)
      return re.test(winHash)
    })
  })
}

export function removeLangFromHash() {
  return getGlobals(({ win }) => {
    const lang = getLangInHash()
    const re = new RegExp(`-${lang}$`)
    return {
      hash: win.location.hash.replace(re, ''),
      lang,
    }
  })
}
