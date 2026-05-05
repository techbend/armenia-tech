<script>
  import { createEventDispatcher } from 'svelte'

  export let source
  export let selectedFeeds = new Set()

  const dispatch = createEventDispatcher()

  let dropdownOpen = false
  let dropdownEl

  function toggleFeed(url) {
    if (selectedFeeds.has(url)) {
      selectedFeeds.delete(url)
    } else {
      selectedFeeds.add(url)
    }
    selectedFeeds = selectedFeeds
  }

  function toggleAll() {
    const allSelected = source.rss_feeds.every(f => selectedFeeds.has(f.url))
    if (allSelected) {
      source.rss_feeds.forEach(f => selectedFeeds.delete(f.url))
    } else {
      source.rss_feeds.forEach(f => selectedFeeds.add(f.url))
    }
    selectedFeeds = selectedFeeds
  }

  function dispatchTagClick(tag) {
    dispatch('tagClick', tag)
  }

  function toggleDropdown(e) {
    e.stopPropagation()
    dropdownOpen = !dropdownOpen
  }

  function handleWindowClick(e) {
    if (dropdownEl && !dropdownEl.contains(e.target)) {
      dropdownOpen = false
    }
  }

  $: hasRss = source.rss_feeds && source.rss_feeds.length > 0
  $: singleFeed = hasRss && source.rss_feeds.length === 1
  $: multiFeed = hasRss && source.rss_feeds.length > 1
  $: anySelected = hasRss && source.rss_feeds.some(f => selectedFeeds.has(f.url))
</script>

<svelte:window on:click={handleWindowClick} />

<article class="{anySelected ? 'ring-1 ring-accent-500/30' : ''} group relative bg-surface-900 border border-surface-800 rounded-xl transition-all duration-300 hover:border-surface-700 hover:shadow-lg hover:shadow-accent-500/5 h-full flex flex-col">
  <!-- Top accent line on hover -->
  <div class="absolute top-0 left-0 right-0 h-0.5 bg-accent-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left rounded-t-xl"></div>

  <div class="p-5 flex flex-col h-full">
    <!-- Header (fixed height area) -->
    <div class="flex items-start justify-between gap-3 mb-3 shrink-0">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="inline-flex items-center px-2 py-0.5 rounded-md bg-accent-500/10 text-accent-400 text-[11px] font-semibold uppercase tracking-wider border border-accent-500/20">
          {source.category}
        </span>
        {#if hasRss}
          <span class="inline-flex items-center px-2 py-0.5 rounded-md bg-rss-500/10 text-rss-400 text-[11px] font-semibold uppercase tracking-wider border border-rss-500/20">
            {source.rss_feeds.length} feeds
          </span>
        {/if}
      </div>
      <span class="text-[11px] font-medium text-surface-500 uppercase tracking-wider shrink-0">
        {source.language}
      </span>
    </div>

    <!-- Title (fixed max 2 lines) -->
    <h2 class="text-base font-semibold text-white leading-snug mb-1 group-hover:text-accent-400 transition-colors line-clamp-2 min-h-[2.5rem]">
      {source.title}
    </h2>

    <!-- Country (single line) -->
    <p class="text-xs text-surface-500 mb-3 shrink-0">{source.country}</p>

    <!-- Description (exactly 3 lines, always) -->
    <p class="text-sm text-surface-400 leading-relaxed mb-4 line-clamp-3 min-h-[3.75rem]">
      {source.description}
    </p>

    <!-- Tags (exactly 1 line, overflow hidden) -->
    {#if source.tags && source.tags.length > 0}
      <div class="flex flex-wrap gap-1.5 mb-4 shrink-0 overflow-hidden h-6">
        {#each source.tags as tag}
          <button
            class="px-2 py-0.5 rounded-md bg-surface-800 hover:bg-surface-700 text-surface-400 hover:text-white text-[11px] font-medium transition-colors border border-transparent hover:border-surface-600 shrink-0"
            on:click={() => dispatchTagClick(tag)}>
            {tag}
          </button>
        {/each}
      </div>
    {:else}
      <div class="h-6 mb-4 shrink-0"></div>
    {/if}

    <!-- Spacer pushes actions to bottom -->
    <div class="flex-1"></div>

    <!-- Actions (pinned to bottom) -->
    <div class="flex gap-2 shrink-0">
      <a
        href={source.website_url}
        target="_blank"
        rel="noopener"
        class="{hasRss ? 'flex-1' : 'w-full'} inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-surface-800 hover:bg-surface-700 text-surface-300 hover:text-white text-sm font-medium transition-all border border-surface-700 hover:border-surface-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
        Visit
      </a>

      {#if singleFeed}
        {@const feed = source.rss_feeds[0]}
        <label class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-rss-500/10 hover:bg-rss-500/20 text-rss-400 hover:text-rss-300 text-sm font-medium transition-all border border-rss-500/20 hover:border-rss-500/30 cursor-pointer">
          <input
            type="checkbox"
            class="peer sr-only"
            checked={selectedFeeds.has(feed.url)}
            on:change={() => toggleFeed(feed.url)}
          />
          <div class="w-4 h-4 rounded border-2 border-rss-500/50 peer-checked:bg-accent-500 peer-checked:border-accent-500 transition-all flex items-center justify-center shrink-0">
            <svg class="w-2.5 h-2.5 text-white opacity-0 peer-checked:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
          </div>
          <span>Feed</span>
        </label>
      {:else if multiFeed}
        {@const allSelected = source.rss_feeds.every(f => selectedFeeds.has(f.url))}
        <div class="flex-1 flex rounded-lg bg-rss-500/10 border border-rss-500/20 hover:border-rss-500/30 transition-all">
          <!-- Select-all checkbox -->
          <label class="flex items-center px-3 py-2 cursor-pointer border-r border-rss-500/20 hover:bg-rss-500/20 rounded-l-lg transition-colors shrink-0">
            <input
              type="checkbox"
              class="peer sr-only"
              checked={allSelected}
              on:change={toggleAll}
            />
            <div class="w-4 h-4 rounded border-2 border-rss-500/50 peer-checked:bg-accent-500 peer-checked:border-accent-500 transition-all flex items-center justify-center">
              <svg class="w-2.5 h-2.5 text-white opacity-0 peer-checked:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
            </div>
          </label>
          <!-- Dropdown trigger -->
          <div class="flex-1 relative" bind:this={dropdownEl}>
            <button type="button" on:click={toggleDropdown} class="w-full inline-flex items-center justify-center gap-1.5 px-3 py-2 text-rss-400 hover:text-rss-300 text-sm font-medium rounded-r-lg hover:bg-rss-500/20 transition-colors">
              {source.rss_feeds.length} Feeds
              <svg class="w-3 h-3 opacity-70 transition-transform {dropdownOpen ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
            {#if dropdownOpen}
              <ul class="absolute bottom-full left-0 right-0 mb-1.5 z-30 p-1.5 shadow-xl bg-surface-900 rounded-xl border border-surface-700 max-h-56 overflow-y-auto">
                {#each source.rss_feeds as feed}
                  <li class="rounded-lg hover:bg-surface-800">
                    <label class="flex items-center gap-2.5 px-3 py-2 cursor-pointer text-surface-300 hover:text-white transition-colors rounded-lg">
                      <div class="relative shrink-0">
                        <input
                          type="checkbox"
                          class="peer sr-only"
                          checked={selectedFeeds.has(feed.url)}
                          on:change={() => toggleFeed(feed.url)}
                        />
                        <div class="w-4 h-4 rounded border-2 border-surface-600 peer-checked:bg-accent-500 peer-checked:border-accent-500 transition-all flex items-center justify-center">
                          <svg class="w-2.5 h-2.5 text-white opacity-0 peer-checked:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                        </div>
                      </div>
                      <a
                        href={feed.url}
                        target="_blank"
                        rel="noopener"
                        class="text-sm truncate hover:text-accent-400 transition-colors"
                        on:click|stopPropagation>
                        {feed.label || 'Feed'}
                      </a>
                    </label>
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  </div>
</article>
