<script>
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
</script>

<div>
  <div class="flex items-center justify-between mb-2">
    <span class="text-[11px] font-bold uppercase tracking-widest text-surface-500">{title}</span>
    {#if selected.length > 0}
      <button
        class="text-[10px] text-surface-500 hover:text-accent-400 transition-colors"
        on:click={clear}>
        Clear
      </button>
    {/if}
  </div>
  <div class="flex flex-wrap gap-1.5">
    {#each options as opt}
      <button
        class="px-2.5 py-1 rounded-lg text-xs font-medium transition-all border {
          selected.includes(opt)
            ? 'bg-accent-500/20 text-accent-300 border-accent-500/40'
            : 'bg-surface-950 text-surface-400 border-surface-800 hover:border-surface-600 hover:text-surface-200'
        }"
        on:click={() => toggle(opt)}>
        {opt}
      </button>
    {/each}
  </div>
</div>
