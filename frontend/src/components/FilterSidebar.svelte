<script>
  import { createEventDispatcher } from 'svelte'
  import FilterSelect from './FilterSelect.svelte'

  export let categories = []
  export let mediaTypes = []
  export let countries = []
  export let languages = []
  export let tags = []

  export let filters = {
    search: '',
    category: '',
    type: '',
    country: '',
    language: '',
    tag: '',
    hasRss: false,
  }

  export let selectedCount = 0

  const dispatch = createEventDispatcher()

  function update(key, value) {
    filters = { ...filters, [key]: value }
  }
</script>

<div class="space-y-4">
  <!-- Search -->
  <div class="bg-surface-900 border border-surface-800 rounded-xl p-4">
    <span class="block text-[11px] font-bold uppercase tracking-widest text-surface-500 mb-2">Search</span>
    <div class="relative">
      <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
      <input
        type="text"
        placeholder="Name or description..."
        class="w-full bg-surface-950 border border-surface-800 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder:text-surface-600 focus:outline-none focus:border-accent-500/50 focus:ring-1 focus:ring-accent-500/20 transition-all"
        bind:value={filters.search}
      />
    </div>
  </div>

  <!-- Filters -->
  <div class="bg-surface-900 border border-surface-800 rounded-xl p-4 space-y-4">
    <h3 class="text-[11px] font-bold uppercase tracking-widest text-surface-500">Filters</h3>

    <div class="space-y-3">
      <FilterSelect label="Category" options={categories} bind:value={filters.category} />
      <FilterSelect label="Media Type" options={mediaTypes} bind:value={filters.type} />
      <FilterSelect label="Country" options={countries} bind:value={filters.country} />
      <FilterSelect label="Language" options={languages} bind:value={filters.language} />
      <FilterSelect label="Tag" options={tags} bind:value={filters.tag} />
    </div>

    <label class="flex items-center gap-3 cursor-pointer group py-1">
      <div class="relative">
        <input
          type="checkbox"
          class="peer sr-only"
          checked={filters.hasRss}
          on:change={(e) => update('hasRss', e.target.checked)}
        />
        <div class="w-9 h-5 rounded-full bg-surface-800 peer-checked:bg-accent-600 transition-colors relative">
          <div class="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-transform peer-checked:translate-x-4"></div>
        </div>
      </div>
      <span class="text-sm text-surface-400 group-hover:text-white transition-colors">Only sources with RSS</span>
    </label>
  </div>

  <!-- Export -->
  <div class="bg-surface-900 border border-surface-800 rounded-xl p-4 space-y-3">
    <h3 class="text-[11px] font-bold uppercase tracking-widest text-surface-500">Export</h3>

    {#if selectedCount > 0}
      <div class="flex items-center justify-between bg-accent-500/5 border border-accent-500/20 rounded-lg px-3 py-2">
        <span class="text-xs text-accent-400 font-medium">{selectedCount} selected</span>
        <button class="text-xs text-surface-500 hover:text-white transition-colors" on:click={() => dispatch('clearSelection')}>Clear</button>
      </div>
    {/if}

    <div class="grid grid-cols-2 gap-2">
      <button
        class="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-surface-800 hover:bg-surface-700 text-surface-300 hover:text-white text-xs font-medium transition-all border border-surface-700"
        on:click={() => dispatch('exportJson')}>
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
        JSON
      </button>
      <button
        class="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-rss-500/10 hover:bg-rss-500/20 text-rss-400 hover:text-rss-300 text-xs font-medium transition-all border border-rss-500/20"
        on:click={() => dispatch('exportOpml')}>
        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M6.503 20.752c0 2.07-1.678 3.748-3.749 3.748s-3.749-1.679-3.749-3.748c0-2.071 1.678-3.749 3.749-3.749s3.749 1.678 3.749 3.749zm-3.749-11.26c-4.627 0-8.373 3.747-8.373 8.373h3.748c0-2.572 2.054-4.625 4.625-4.625v-3.748zm0-4.627c-7.03 0-12.752 5.722-12.752 12.752h3.748c0-4.972 4.032-9.004 9.004-9.004v-3.748z"/></svg>
        OPML
      </button>
    </div>
  </div>
</div>
