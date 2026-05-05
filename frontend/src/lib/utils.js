export function escapeXml(str) {
  if (!str) return ''
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

export function generateOpml(feeds) {
  const byCat = {}
  feeds.forEach(f => {
    byCat[f.category] = byCat[f.category] || []
    byCat[f.category].push(f)
  })

  let xml = `<?xml version="1.0" encoding="UTF-8"?>\n<opml version="1.0">\n  <body>\n`
  Object.entries(byCat).forEach(([catName, catFeeds]) => {
    xml += `    <outline text="${escapeXml(catName)}" title="${escapeXml(catName)}">\n`
    catFeeds.forEach(f => {
      const text = f.feedLabel ? `${f.sourceTitle} - ${f.feedLabel}` : f.sourceTitle
      xml += `      <outline text="${escapeXml(text)}" title="${escapeXml(text)}" type="rss" htmlUrl="${escapeXml(f.websiteUrl)}" xmlUrl="${escapeXml(f.feedUrl)}"/>\n`
    })
    xml += `    </outline>\n`
  })
  xml += `  </body>\n</opml>`
  return xml
}

export function downloadBlob(content, mimeType, filename) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function getUniqueValues(sources, key) {
  const vals = new Set()
  sources.forEach(s => {
    if (key === 'tags') {
      (s.tags || []).forEach(t => vals.add(t))
    } else {
      const v = s[key]
      if (v) vals.add(v)
    }
  })
  return Array.from(vals).sort((a, b) => a.localeCompare(b))
}
