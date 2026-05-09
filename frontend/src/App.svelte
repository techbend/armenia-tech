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
    tag: [],
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
    const matchesTag = filters.tag.length === 0 || (c.tags || []).some(t => filters.tag.includes(t))

    return matchesSearch && matchesOrigin && matchesEmployees && matchesType && matchesTag
  })

  function handleTagClick(tag) {
    if (!filters.tag.includes(tag)) {
      filters = { ...filters, tag: [...filters.tag, tag] }
    }
    sidebarOpen = false
  }

  function clearFilters() {
    filters = {
      search: '',
      origin: [],
      employees: [],
      company_type: [],
      tag: [],
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

<!-- Skip link for keyboard navigation -->
<a href="#main-content" class="sr-only">Skip to main content</a>

<div class="min-h-screen bg-page">
  <!-- Hero Header -->
  <header class="relative bg-white border-b border-border overflow-hidden">
    <!-- Subtle background pattern -->
    <div class="absolute inset-0 opacity-[0.03]" style="background-image: radial-gradient(circle, #0f172a 1px, transparent 1px); background-size: 24px 24px;" aria-hidden="true"></div>
    
    <div class="relative max-w-[1600px] mx-auto px-4 lg:px-8">
      <!-- Top nav bar -->
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-accent-light border border-blue-200 flex items-center justify-center" aria-hidden="true">
            <svg class="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-text-primary tracking-tight">Armenia Tech Landscape</h1>
          </div>
        </div>

        <div class="hidden md:flex items-center gap-6">
          <div class="text-center px-4 py-1.5 rounded-lg bg-surface border border-border">
            <span class="block text-2xl font-bold text-accent">{companies.length}</span>
            <span class="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Companies</span>
          </div>
        </div>

        <button
          class="lg:hidden p-2.5 rounded-xl bg-surface border border-border text-text-secondary hover:text-text-primary hover:bg-white hover:border-border-strong transition-all min-h-[44px] min-w-[44px] flex items-center justify-center"
          on:click={() => sidebarOpen = !sidebarOpen}
          aria-expanded={sidebarOpen}
          aria-controls="filter-sidebar"
          aria-label={sidebarOpen ? 'Close filters' : 'Open filters'}>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
      </div>

      <!-- Hero content -->
      <div class="py-10 pb-12 text-center">
        <h2 class="text-3xl sm:text-4xl font-bold text-text-primary mb-3 tracking-tight">
          Discover Armenian Tech
        </h2>
        <p class="text-base sm:text-lg text-text-secondary max-w-2xl mx-auto mb-8 leading-relaxed">
          A curated directory of tech companies — from Yerevan startups to global enterprises founded by Armenians.
        </p>

        <!-- Inline search for quick access -->
        <div class="max-w-xl mx-auto relative">
          <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <input
            type="text"
            placeholder="Search companies by name or description..."
            class="w-full bg-surface border border-border rounded-2xl pl-12 pr-4 py-3.5 text-base text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-4 focus:ring-accent-light/50 transition-all shadow-sm"
            bind:value={filters.search}
          />
        </div>
      </div>
    </div>
  </header>

  <!-- Mobile Sidebar Overlay -->
  {#if sidebarOpen}
    <button type="button" class="fixed inset-0 z-40 bg-black/20 lg:hidden cursor-default" on:click={() => sidebarOpen = false} aria-label="Close sidebar overlay"></button>
  {/if}

  <!-- Main Content -->
  <main id="main-content" class="max-w-[1600px] mx-auto px-4 lg:px-8 py-8">
    {#if loading}
      <div class="flex flex-col items-center justify-center py-32 gap-4" role="status" aria-live="polite">
        <div class="relative w-12 h-12">
          <div class="absolute inset-0 rounded-full border-2 border-border"></div>
          <div class="absolute inset-0 rounded-full border-2 border-accent border-t-transparent animate-spin"></div>
        </div>
        <p class="text-text-muted text-sm">Loading catalog...</p>
      </div>
    {:else if error}
      <div class="max-w-md mx-auto mt-20 text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center" aria-hidden="true">
          <svg class="w-8 h-8 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        </div>
        <h2 class="text-xl font-semibold text-text-primary mb-2">Failed to load</h2>
        <p class="text-text-secondary">{error}</p>
      </div>
    {:else}
      <div class="flex gap-8">
        <!-- Sidebar -->
        <div id="filter-sidebar" class="{sidebarOpen ? 'fixed inset-y-0 left-0 z-50 w-80 bg-white border-r border-border overflow-y-auto p-5 shadow-xl' : 'hidden'} lg:block lg:static lg:w-72 lg:flex-shrink-0 lg:bg-transparent lg:border-0 lg:p-0 lg:shadow-none lg:overflow-visible">
          <div class="lg:sticky lg:top-8">
            {#if sidebarOpen}
              <div class="flex items-center justify-between mb-5 lg:hidden">
                <h2 class="text-lg font-bold text-text-primary">Filters</h2>
                <button class="p-2.5 rounded-xl bg-surface border border-border text-text-secondary hover:text-text-primary min-h-[44px] min-w-[44px] flex items-center justify-center" on:click={() => sidebarOpen = false} aria-label="Close filters">
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
          <!-- Active filters bar -->
          {#if filters.search || filters.origin.length || filters.employees.length || filters.company_type.length || filters.tag.length}
            <div class="flex flex-wrap items-center gap-2 mb-5 p-3 bg-surface rounded-xl border border-border">
              <span class="text-xs font-semibold text-text-muted uppercase tracking-wider">Active:</span>
              {#if filters.search}
                <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-border text-xs text-text-secondary">
                  Search: "{filters.search}"
                  <button class="ml-1 text-text-muted hover:text-error" on:click={() => filters.search = ''} aria-label="Remove search filter">×</button>
                </span>
              {/if}
              {#each filters.origin as o}
                <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-border text-xs text-text-secondary">
                  {o}
                  <button class="ml-1 text-text-muted hover:text-error" on:click={() => filters.origin = filters.origin.filter(x => x !== o)} aria-label="Remove {o} filter">×</button>
                </span>
              {/each}
              {#each filters.employees as e}
                <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-border text-xs text-text-secondary">
                  {e}
                  <button class="ml-1 text-text-muted hover:text-error" on:click={() => filters.employees = filters.employees.filter(x => x !== e)} aria-label="Remove {e} filter">×</button>
                </span>
              {/each}
              {#each filters.company_type as t}
                <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-border text-xs text-text-secondary">
                  {t}
                  <button class="ml-1 text-text-muted hover:text-error" on:click={() => filters.company_type = filters.company_type.filter(x => x !== t)} aria-label="Remove {t} filter">×</button>
                </span>
              {/each}
              {#each filters.tag as t}
                <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-border text-xs text-text-secondary">
                  {t}
                  <button class="ml-1 text-text-muted hover:text-error" on:click={() => filters.tag = filters.tag.filter(x => x !== t)} aria-label="Remove {t} filter">×</button>
                </span>
              {/each}
              <button
                class="text-xs text-text-muted hover:text-accent transition-colors ml-auto px-2 py-1"
                on:click={clearFilters}>
                Clear all
              </button>
            </div>
          {/if}

          <!-- Results header -->
          <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
            <p class="text-sm text-text-secondary" aria-live="polite">
              Showing <span class="font-bold text-text-primary">{filteredCompanies.length}</span> of <span class="font-bold text-text-primary">{companies.length}</span> companies
            </p>
          </div>

          {#if filteredCompanies.length === 0}
            <div class="text-center py-24 animate-fade-in">
              <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-surface border border-border flex items-center justify-center" aria-hidden="true">
                <svg class="w-10 h-10 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              </div>
              <h3 class="text-lg font-semibold text-text-primary mb-1">No matches found</h3>
              <p class="text-text-secondary text-sm">Try adjusting your filters or search terms.</p>
            </div>
          {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 items-stretch">
              {#each filteredCompanies as company, i (company.name)}
                <div class="animate-slide-up h-full" style="animation-delay: {Math.min(i * 40, 300)}ms; animation-fill-mode: both;">
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
  <footer class="border-t border-border mt-20 bg-surface">
    <div class="max-w-[1600px] mx-auto px-4 lg:px-8 py-10 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-accent-light border border-blue-200 flex items-center justify-center" aria-hidden="true">
          <svg class="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
        </div>
        <p class="text-sm text-text-muted">
          Armenia Tech Landscape
        </p>
      </div>
      <div class="flex items-center gap-5 text-sm text-text-muted">
        <a href="data.json" download class="hover:text-accent transition-colors underline underline-offset-2 font-medium">Download JSON</a>
      </div>
    </div>
  </footer>
</div>
