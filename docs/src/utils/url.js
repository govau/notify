import { languages } from '../config'

export function getLangInHash() {
  const winHash = window.location.hash
  return Object.keys(languages).find(lang => {
    const re = new RegExp(`-${lang}$`)
    return re.test(winHash)
  })
}

export function removeLangFromHash() {
  const lang = getLangInHash()
  const re = new RegExp(`-${lang}$`)
  return {
    hash: window.location.hash.replace(re, ''),
    lang,
  }
}
