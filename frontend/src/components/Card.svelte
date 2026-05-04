<script>
  import { createEventDispatcher } from 'svelte'

  export let source
  export let selectedFeeds = new Set()

  const dispatch = createEventDispatcher()

  function toggleFeed(url) {
    if (selectedFeeds.has(url)) {
      selectedFeeds.delete(url)
    } else {
      selectedFeeds.add(url)
    }
    selectedFeeds = selectedFeeds
  }

  function dispatchTagClick(tag) {
    dispatch('tagClick', tag)
  }

  $: hasRss = source.rss_feeds && source.rss_feeds.length > 0
  $: singleFeed = hasRss && source.rss_feeds.length === 1
  $: multiFeed = hasRss && source.rss_feeds.length > 1
  $: anySelected = hasRss && source.rss_feeds.some(f => selectedFeeds.has(f.url))
</script>

<article class="{anySelected ? 'ring-1 ring-accent-500/30' : ''} group relative bg-surface-900 border border-surface-800 rounded-xl overflow-hidden transition-all duration-300 hover:border-surface-700 hover:shadow-lg hover:shadow-accent-500/5 h-full flex flex-col">
  <!-- Top accent line on hover -->
  <div class="absolute top-0 left-0 right-0 h-0.5 bg-accent-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></div>

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
        <a
          href={source.rss_feeds[0].url}
          target="_blank"
          rel="noopener"
          class="flex-1 inline-flex items-center justify-center px-3 py-2 rounded-lg bg-rss-500/10 hover:bg-rss-500/20 text-rss-400 hover:text-rss-300 text-sm font-medium transition-all border border-rss-500/20 hover:border-rss-500/30">
          RSS
        </a>
      {:else if multiFeed}
        <div class="dropdown dropdown-top dropdown-end flex-1">
          <button type="button" class="flex-1 inline-flex items-center justify-center px-3 py-2 rounded-lg bg-rss-500/10 hover:bg-rss-500/20 text-rss-400 hover:text-rss-300 text-sm font-medium transition-all border border-rss-500/20 hover:border-rss-500/30 w-full">
            {source.rss_feeds.length} Feeds
          </button>
          <ul class="dropdown-content z-[1] menu p-2 shadow-xl bg-surface-900 rounded-xl w-56 border border-surface-700">
            {#each source.rss_feeds as feed}
              <li>
                <a href={feed.url} target="_blank" rel="noopener" class="text-surface-300 hover:text-white hover:bg-surface-800 rounded-lg">
                  {feed.label || 'Feed'}
                </a>
              </li>
            {/each}
          </ul>
        </div>
      {/if}
    </div>

    <!-- Feed Selection (always present for consistent height) -->
    <div class="pt-3 border-t border-surface-800/80 mt-3 shrink-0 min-h-[2rem]">
      {#if hasRss}
        <div class="flex flex-wrap gap-x-4 gap-y-2">
          {#each source.rss_feeds as feed}
            <label class="inline-flex items-center gap-2 cursor-pointer group/check">
              <div class="relative">
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
              <span class="text-xs text-surface-500 group-hover/check:text-surface-300 transition-colors">
                {feed.label || 'Select'}
              </span>
            </label>
          {/each}
        </div>
      {:else}
        <div class="h-5"></div>
      {/if}
    </div>
  </div>
</article>
