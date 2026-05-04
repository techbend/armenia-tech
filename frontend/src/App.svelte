<script>
  import { onMount } from 'svelte'
  import FilterSidebar from './components/FilterSidebar.svelte'
  import Card from './components/Card.svelte'
  import { getUniqueValues, generateOpml, downloadBlob } from './lib/utils.js'

  let sources = []
  let loading = true
  let error = null

  let filters = {
    search: '',
    category: '',
    type: '',
    country: '',
    language: '',
    tag: '',
    hasRss: false,
  }

  let selectedFeeds = new Set()
  let sidebarOpen = false

  onMount(async () => {
    try {
      const res = await fetch('./data.json')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      sources = await res.json()
    } catch (e) {
      error = e.message
    } finally {
      loading = false
    }
  })

  $: categories = getUniqueValues(sources, 'category')
  $: mediaTypes = getUniqueValues(sources, 'media_type')
  $: countries = getUniqueValues(sources, 'country')
  $: languages = getUniqueValues(sources, 'language')
  $: allTags = getUniqueValues(sources, 'tags')

  $: filteredSources = sources.filter(s => {
    const term = filters.search.toLowerCase().trim()
    const matchesSearch = !term ||
      s.title.toLowerCase().includes(term) ||
      (s.description || '').toLowerCase().includes(term)
    const matchesCategory = !filters.category || s.category === filters.category
    const matchesType = !filters.type || s.media_type === filters.type
    const matchesCountry = !filters.country || s.country === filters.country
    const matchesLang = !filters.language || s.language === filters.language
    const matchesTag = !filters.tag || (s.tags || []).includes(filters.tag)
    const matchesRss = !filters.hasRss || (s.rss_feeds && s.rss_feeds.length > 0)

    return matchesSearch && matchesCategory && matchesType && matchesCountry && matchesLang && matchesTag && matchesRss
  })

  $: selectedCount = selectedFeeds.size
  $: totalFeeds = sources.reduce((sum, s) => sum + (s.rss_feeds?.length || 0), 0)
  $: feedCount = filteredSources.reduce((sum, s) => sum + (s.rss_feeds?.length || 0), 0)

  function handleTagClick(tag) {
    filters = { ...filters, tag }
    sidebarOpen = false
  }

  function clearSelection() {
    selectedFeeds = new Set()
  }

  function clearFilters() {
    filters = {
      search: '',
      category: '',
      type: '',
      country: '',
      language: '',
      tag: '',
      hasRss: false,
    }
  }

  function getFeedsToExport() {
    if (selectedFeeds.size > 0) {
      const feeds = []
      sources.forEach(s => {
        if (s.rss_feeds) {
          s.rss_feeds.forEach(f => {
            if (selectedFeeds.has(f.url)) {
              feeds.push({
                sourceTitle: s.title,
                feedUrl: f.url,
                feedLabel: f.label || '',
                category: s.category,
                websiteUrl: s.website_url,
              })
            }
          })
        }
      })
      return feeds
    }

    const feeds = []
    filteredSources.forEach(s => {
      if (s.rss_feeds) {
        s.rss_feeds.forEach(f => {
          feeds.push({
            sourceTitle: s.title,
            feedUrl: f.url,
            feedLabel: f.label || '',
            category: s.category,
            websiteUrl: s.website_url,
          })
        })
      }
    })
    return feeds
  }

  function exportJson() {
    const feeds = getFeedsToExport()
    if (feeds.length === 0) {
      alert('No RSS feeds to export.')
      return
    }
    const filename = selectedFeeds.size > 0
      ? 'awesome_media_selected.json'
      : 'awesome_media_filtered.json'
    downloadBlob(JSON.stringify(feeds, null, 2), 'application/json', filename)
  }

  function exportOpml() {
    const feeds = getFeedsToExport()
    if (feeds.length === 0) {
      alert('No RSS feeds to export.')
      return
    }
    const xml = generateOpml(feeds)
    const filename = selectedFeeds.size > 0
      ? 'awesome_media_selected.opml'
      : 'awesome_media_filtered.opml'
    downloadBlob(xml, 'application/xml', filename)
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
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-white tracking-tight">Awesome Media</h1>
          </div>
        </div>

        <!-- Stats -->
        <div class="hidden md:flex items-center gap-6">
          <div class="text-center">
            <span class="block text-xl font-bold text-white">{sources.length}</span>
            <span class="text-[10px] uppercase tracking-widest text-surface-500 font-medium">Sources</span>
          </div>
          <div class="w-px h-8 bg-surface-800"></div>
          <div class="text-center">
            <span class="block text-xl font-bold text-accent-400">{totalFeeds}</span>
            <span class="text-[10px] uppercase tracking-widest text-surface-500 font-medium">Feeds</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2">
          <a href="feeds.opml" download class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-800 hover:bg-surface-700 text-surface-300 hover:text-white text-sm font-medium transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            OPML
          </a>
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
              {categories}
              {mediaTypes}
              {countries}
              {languages}
              tags={allTags}
              bind:filters
              {selectedCount}
              on:clearSelection={clearSelection}
              on:exportJson={exportJson}
              on:exportOpml={exportOpml}
            />
          </div>
        </div>

        <!-- Results -->
        <div class="flex-1 min-w-0">
          <!-- Results Bar -->
          <div class="flex flex-wrap items-center justify-between gap-3 mb-5">
            <div class="flex items-center gap-3">
              <span class="text-sm text-surface-400">
                Showing <strong class="text-white">{filteredSources.length}</strong> of <strong class="text-white">{sources.length}</strong> sources
              </span>
              {#if feedCount > 0}
                <span class="hidden sm:inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-accent-500/10 text-accent-400 border border-accent-500/20 font-medium">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 5c7.18 0 13 5.82 13 13M6 11a7 7 0 017 7m-6 0a1 1 0 11-2 0 1 1 0 012 0z"/></svg>
                  {feedCount} feeds
                </span>
              {/if}
            </div>

            {#if filters.search || filters.category || filters.type || filters.country || filters.language || filters.tag || filters.hasRss}
              <button
                class="text-xs text-surface-500 hover:text-accent-400 transition-colors flex items-center gap-1"
                on:click={clearFilters}>
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                Clear filters
              </button>
            {/if}
          </div>

          {#if filteredSources.length === 0}
            <div class="text-center py-24 animate-fade-in">
              <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-surface-900 border border-surface-800 flex items-center justify-center">
                <svg class="w-10 h-10 text-surface-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              </div>
              <h3 class="text-lg font-semibold text-white mb-1">No matches found</h3>
              <p class="text-surface-500 text-sm">Try adjusting your filters or search terms.</p>
            </div>
          {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 items-stretch">
              {#each filteredSources as source, i (source.title)}
                <div class="animate-slide-up h-full" style="animation-delay: {Math.min(i * 30, 300)}ms; animation-fill-mode: both;">
                  <Card
                    {source}
                    bind:selectedFeeds
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
        Awesome Media Catalog — Curated news, podcasts, and independent sources.
      </p>
      <div class="flex items-center gap-4 text-sm text-surface-600">
        <a href="data.json" download class="hover:text-accent-400 transition-colors">JSON</a>
        <a href="feeds.opml" download class="hover:text-accent-400 transition-colors">OPML</a>
      </div>
    </div>
  </footer>
</div>
