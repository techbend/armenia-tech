/**
 * Accessible badge colors + fill patterns for color blindness support.
 * WCAG 2.0 SC 1.4.1: Color is not used as the only visual means of
 * conveying information.
 *
 * Each label value gets a unique color + pattern combination.
 */

const PATTERNS = {
  solid: '',
  'h-stripes': `repeating-linear-gradient(
    0deg, transparent, transparent 5px, rgba(0,0,0,0.06) 5px, rgba(0,0,0,0.06) 10px
  )`,
  'd-stripes': `repeating-linear-gradient(
    45deg, transparent, transparent 5px, rgba(0,0,0,0.05) 5px, rgba(0,0,0,0.05) 10px
  )`,
  dots: `radial-gradient(circle, rgba(0,0,0,0.1) 1.5px, transparent 1.5px)`,
  'v-lines': `repeating-linear-gradient(
    90deg, transparent, transparent 5px, rgba(0,0,0,0.06) 5px, rgba(0,0,0,0.06) 10px
  )`,
  checks: `repeating-linear-gradient(0deg, transparent, transparent 6px, rgba(0,0,0,0.04) 6px, rgba(0,0,0,0.04) 12px),
           repeating-linear-gradient(90deg, transparent, transparent 6px, rgba(0,0,0,0.04) 6px, rgba(0,0,0,0.04) 12px)`,
}

function makeStyle(bg, text, border, patternKey) {
  const pattern = PATTERNS[patternKey]
  return {
    bg,
    text,
    border,
    pattern,
    patternSize: patternKey === 'dots' ? '10px 10px' : 'auto',
  }
}

export const BADGE_COLORS = {
  // ─── Origin ───
  local:  makeStyle('#ecfdf5', '#047857', '#a7f3d0', 'solid'),
  global: makeStyle('#eff6ff', '#1d4ed8', '#bfdbfe', 'h-stripes'),

  // ─── Employees ───
  '1-10':    makeStyle('#fffbeb', '#b45309', '#fde68a', 'd-stripes'),
  '11-50':   makeStyle('#fff7ed', '#c2410c', '#fed7aa', 'dots'),
  '51-100':  makeStyle('#f0fdfa', '#0f766e', '#99f6e4', 'v-lines'),
  '101-250': makeStyle('#eef2ff', '#4338ca', '#c7d2fe', 'checks'),
  '251-500': makeStyle('#f5f3ff', '#6d28d9', '#ddd6fe', 'solid'),
  '+500':    makeStyle('#fff1f2', '#be123c', '#fecdd3', 'h-stripes'),

  // ─── Company Type ───
  service: makeStyle('#ecfeff', '#0e7490', '#a5f3fc', 'd-stripes'),
  product: makeStyle('#fdf4ff', '#a21caf', '#f0abfc', 'dots'),
}

export function getBadgeStyle(value) {
  return BADGE_COLORS[value] || makeStyle('#f1f5f9', '#334155', '#e2e8f0', 'solid')
}
