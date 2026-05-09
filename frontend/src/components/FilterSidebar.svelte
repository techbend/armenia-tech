<script>
  import { createEventDispatcher } from 'svelte'
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
    tag: [],
  }

  const dispatch = createEventDispatcher()
</script>

<div class="space-y-5">
  <!-- Filters Panel -->
  <div class="bg-white border border-border rounded-2xl p-5 space-y-5 shadow-sm">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-bold text-text-primary">Filters</h3>
      <button
        class="text-xs text-text-muted hover:text-accent transition-colors px-2 py-1 rounded"
        on:click={() => dispatch('clearFilters')}>
        Reset
      </button>
    </div>

    <FilterCheckboxGroup title="Origin" options={origins} bind:selected={filters.origin} />
    <FilterCheckboxGroup title="Employees" options={employeeRanges} bind:selected={filters.employees} />
    <FilterCheckboxGroup title="Company Type" options={companyTypes} bind:selected={filters.company_type} />

    <div class="pt-3 border-t border-border">
      <FilterCheckboxGroup title="Tags" options={tags} bind:selected={filters.tag} />
    </div>
  </div>

  <!-- Export Panel -->
  <div class="bg-white border border-border rounded-2xl p-5 shadow-sm">
    <h3 class="text-sm font-bold text-text-primary mb-3">Export</h3>
    <button
      class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-surface hover:bg-white text-text-secondary hover:text-text-primary text-sm font-medium transition-all border border-border hover:border-border-strong min-h-[44px]"
      on:click={() => dispatch('exportJson')}>
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
      Export as JSON
    </button>
  </div>
</div>
