<script>
  import { getBadgeStyle } from '../lib/badgeColors.js'

  export let title = ''
  export let options = []
  export let selected = []

  function toggle(value) {
    if (selected.includes(value)) {
      selected = selected.filter(v => v !== value)
    } else {
      selected = [...selected, value]
    }
  }

  function clear() {
    selected = []
  }

  function pillStyle(value, isSelected) {
    const s = getBadgeStyle(value)
    const parts = []

    if (isSelected) {
      parts.push(`background-color: ${s.text}`)
      parts.push(`color: #ffffff`)
      parts.push(`border-color: ${s.text}`)
      // Keep pattern visible on dark bg by inverting to white
      if (s.pattern) {
        const whitePattern = s.pattern.replace(/rgba\(0,0,0,([0-9.]+)\)/g, 'rgba(255,255,255,$1)')
        parts.push(`background-image: ${whitePattern}`)
        if (s.patternSize) parts.push(`background-size: ${s.patternSize}`)
      }
    } else {
      parts.push(`background-color: ${s.bg}`)
      parts.push(`color: ${s.text}`)
      parts.push(`border-color: ${s.border}`)
      if (s.pattern) {
        parts.push(`background-image: ${s.pattern}`)
        if (s.patternSize) parts.push(`background-size: ${s.patternSize}`)
      }
    }

    return parts.join('; ')
  }
</script>

<div>
  <div class="flex items-center justify-between mb-2">
    <span class="text-[11px] font-bold uppercase tracking-widest text-text-muted">{title}</span>
    {#if selected.length > 0}
      <button
        class="text-[10px] text-text-muted hover:text-accent transition-colors px-1 py-0.5 rounded"
        on:click={clear}>
        Clear
      </button>
    {/if}
  </div>
  <div class="flex flex-wrap gap-1.5" role="group" aria-label="{title} filter options">
    {#each options as opt}
      {@const isSelected = selected.includes(opt)}
      <button
        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all border min-h-[36px]"
        style={pillStyle(opt, isSelected)}
        aria-pressed={isSelected}
        on:click={() => toggle(opt)}>
        {opt}
      </button>
    {/each}
  </div>
</div>
