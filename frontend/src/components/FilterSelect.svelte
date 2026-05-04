<script>
  export let label
  export let options = []
  export let value = ''
</script>

<div>
  <span class="block text-[10px] font-semibold uppercase tracking-wider text-surface-600 mb-1.5">{label}</span>
  <div class="relative">
    <select
      class="w-full appearance-none bg-surface-950 border border-surface-800 rounded-lg px-3 py-2 pr-8 text-sm text-white focus:outline-none focus:border-accent-500/50 focus:ring-1 focus:ring-accent-500/20 transition-all cursor-pointer"
      bind:value>
      <option value="">All {label}s</option>
      {#each options as opt}
        <option value={opt}>{opt}</option>
      {/each}
    </select>
    <svg class="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-600 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
  </div>
</div>
