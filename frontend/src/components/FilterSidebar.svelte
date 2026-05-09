<script>
  import { createEventDispatcher } from 'svelte'
  import FilterSelect from './FilterSelect.svelte'
  import FilterCheckboxGroup from './FilterCheckboxGroup.svelte'

  export let origins = []
  export let employeeRanges = []
  export let companyTypes = []
  export let tags = []

  export let filters = {
    search: '',
    origin: [],
    employees: [],
    company_type: [],
    tag: '',
  }

  const dispatch = createEventDispatcher()
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
    <div class="flex items-center justify-between">
      <h3 class="text-[11px] font-bold uppercase tracking-widest text-surface-500">Filters</h3>
      <button
        class="text-[11px] text-surface-500 hover:text-accent-400 transition-colors"
        on:click={() => dispatch('clearFilters')}>
        Clear all
      </button>
    </div>

    <FilterCheckboxGroup title="Origin" options={origins} bind:selected={filters.origin} />
    <FilterCheckboxGroup title="Employees" options={employeeRanges} bind:selected={filters.employees} />
    <FilterCheckboxGroup title="Company Type" options={companyTypes} bind:selected={filters.company_type} />

    <div class="pt-2 border-t border-surface-800">
      <FilterSelect label="Tag" options={tags} bind:value={filters.tag} />
    </div>
  </div>

  <!-- Export -->
  <div class="bg-surface-900 border border-surface-800 rounded-xl p-4 space-y-3">
    <h3 class="text-[11px] font-bold uppercase tracking-widest text-surface-500">Export</h3>

    <button
      class="w-full inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-surface-800 hover:bg-surface-700 text-surface-300 hover:text-white text-xs font-medium transition-all border border-surface-700"
      on:click={() => dispatch('exportJson')}>
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
      JSON
    </button>
  </div>
</div>
