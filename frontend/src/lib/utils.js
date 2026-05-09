export function downloadBlob(content, mimeType, filename) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function getUniqueValues(companies, key) {
  const vals = new Set()
  companies.forEach(c => {
    const v = c[key]
    if (Array.isArray(v)) {
      v.forEach(item => { if (item) vals.add(item) })
    } else if (v) {
      vals.add(v)
    }
  })
  return Array.from(vals).sort((a, b) => a.localeCompare(b))
}
