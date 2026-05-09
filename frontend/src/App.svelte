<script>
  import { onMount } from 'svelte'
  import FilterSidebar from './components/FilterSidebar.svelte'
  import Card from './components/Card.svelte'
  import { getUniqueValues, downloadBlob } from './lib/utils.js'

  let companies = []
  let loading = true
  let error = null

  let filters = {
    search: '',
    origin: [],
    employees: [],
    company_type: [],
    tag: '',
  }

  let sidebarOpen = false

  onMount(async () => {
    try {
      const res = await fetch('./data.json')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      companies = await res.json()
    } catch (e) {
      error = e.message
    } finally {
      loading = false
    }
  })

  $: origins = getUniqueValues(companies, 'origin')
  $: employeeRanges = getUniqueValues(companies, 'employees')
  $: companyTypes = getUniqueValues(companies, 'company_type')
  $: allTags = getUniqueValues(companies, 'tags')

  $: filteredCompanies = companies.filter(c => {
    const term = filters.search.toLowerCase().trim()
    const matchesSearch = !term ||
      c.name.toLowerCase().includes(term) ||
      (c.description || '').toLowerCase().includes(term)

    const matchesOrigin = filters.origin.length === 0 || (c.origin || []).some(o => filters.origin.includes(o))
    const matchesEmployees = filters.employees.length === 0 || filters.employees.includes(c.employees)
    const matchesType = filters.company_type.length === 0 || (c.company_type || []).some(t => filters.company_type.includes(t))
    const matchesTag = !filters.tag || (c.tags || []).includes(filters.tag)

    return matchesSearch && matchesOrigin && matchesEmployees && matchesType && matchesTag
  })

  function handleTagClick(tag) {
    filters = { ...filters, tag }
    sidebarOpen = false
  }

  function clearFilters() {
    filters = {
      search: '',
      origin: [],
      employees: [],
      company_type: [],
      tag: '',
    }
  }

  function exportJson() {
    const data = filteredCompanies.length > 0 && filteredCompanies.length !== companies.length
      ? filteredCompanies
      : companies
    const filename = filteredCompanies.length !== companies.length
      ? 'armenia_tech_filtered.json'
      : 'armenia_tech.json'
    downloadBlob(JSON.stringify(data, null, 2), 'application/json', filename)
  }
</script>

<div class="min-h-screen bg-surface-950">
  <!-- Header -->
  <header class="sticky top-0 z-50 bg-surface-950/80 backdrop-blur-xl border-b border-surface-800">
    <div class="max-w-[1600px] mx-auto px-4 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-accent-500/10 border border-accent-500/20 flex items-center justify-center">
            <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-white tracking-tight">Armenia Tech Landscape</h1>
          </div>
        </div>

        <!-- Stats -->
        <div class="hidden md:flex items-center gap-6">
          <div class="text-center">
            <span class="block text-xl font-bold text-white">{companies.length}</span>
            <span class="text-[10px] uppercase tracking-widest text-surface-500 font-medium">Companies</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2">
          <button
            class="lg:hidden p-2 rounded-lg bg-surface-800 text-surface-300 hover:text-white"
            on:click={() => sidebarOpen = !sidebarOpen}>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Mobile Sidebar Overlay -->
  {#if sidebarOpen}
    <button type="button" class="fixed inset-0 z-40 bg-black/50 lg:hidden cursor-default" on:click={() => sidebarOpen = false} aria-label="Close sidebar"></button>
  {/if}

  <!-- Main Content -->
  <main class="max-w-[1600px] mx-auto px-4 lg:px-8 py-6">
    {#if loading}
      <div class="flex flex-col items-center justify-center py-32 gap-4">
        <div class="relative w-12 h-12">
          <div class="absolute inset-0 rounded-full border-2 border-surface-800"></div>
          <div class="absolute inset-0 rounded-full border-2 border-accent-500 border-t-transparent animate-spin"></div>
        </div>
        <p class="text-surface-500 text-sm">Loading catalog...</p>
      </div>
    {:else if error}
      <div class="max-w-md mx-auto mt-20 text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-error/10 border border-error/20 flex items-center justify-center">
          <svg class="w-8 h-8 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        </div>
        <h2 class="text-xl font-semibold text-white mb-2">Failed to load</h2>
        <p class="text-surface-500">{error}</p>
      </div>
    {:else}
      <div class="flex gap-6">
        <!-- Sidebar -->
        <div class="{sidebarOpen ? 'fixed inset-y-0 left-0 z-50 w-80 bg-surface-950 border-r border-surface-800 overflow-y-auto p-4' : 'hidden'} lg:block lg:static lg:w-72 lg:flex-shrink-0 lg:bg-transparent lg:border-0 lg:p-0 lg:overflow-visible">
          <div class="lg:sticky lg:top-24">
            {#if sidebarOpen}
              <div class="flex items-center justify-between mb-4 lg:hidden">
                <h2 class="text-lg font-semibold text-white">Filters</h2>
                <button class="p-2 rounded-lg bg-surface-800 text-surface-400" on:click={() => sidebarOpen = false}>
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>
            {/if}

            <FilterSidebar
              {origins}
              {employeeRanges}
              {companyTypes}
              tags={allTags}
              bind:filters
              on:clearFilters={clearFilters}
              on:exportJson={exportJson}
            />
          </div>
        </div>

        <!-- Results -->
        <div class="flex-1 min-w-0">
          <!-- Results Bar -->
          <div class="flex flex-wrap items-center justify-between gap-3 mb-5">
            <div class="flex items-center gap-3">
              <span class="text-sm text-surface-400">
                Showing <strong class="text-white">{filteredCompanies.length}</strong> of <strong class="text-white">{companies.length}</strong> companies
              </span>
            </div>

            {#if filters.search || filters.origin.length || filters.employees.length || filters.company_type.length || filters.tag}
              <button
                class="text-xs text-surface-500 hover:text-accent-400 transition-colors flex items-center gap-1"
                on:click={clearFilters}>
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                Clear filters
              </button>
            {/if}
          </div>

          {#if filteredCompanies.length === 0}
            <div class="text-center py-24 animate-fade-in">
              <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-surface-900 border border-surface-800 flex items-center justify-center">
                <svg class="w-10 h-10 text-surface-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              </div>
              <h3 class="text-lg font-semibold text-white mb-1">No matches found</h3>
              <p class="text-surface-500 text-sm">Try adjusting your filters or search terms.</p>
            </div>
          {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 items-stretch">
              {#each filteredCompanies as company, i (company.name)}
                <div class="animate-slide-up h-full" style="animation-delay: {Math.min(i * 30, 300)}ms; animation-fill-mode: both;">
                  <Card
                    {company}
                    on:tagClick={(e) => handleTagClick(e.detail)}
                  />
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </main>

  <!-- Footer -->
  <footer class="border-t border-surface-800 mt-16">
    <div class="max-w-[1600px] mx-auto px-4 lg:px-8 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
      <p class="text-sm text-surface-600">
        Armenia Tech Landscape — Curated directory of Armenian tech companies.
      </p>
      <div class="flex items-center gap-4 text-sm text-surface-600">
        <a href="data.json" download class="hover:text-accent-400 transition-colors">JSON</a>
      </div>
    </div>
  </footer>
</div>
