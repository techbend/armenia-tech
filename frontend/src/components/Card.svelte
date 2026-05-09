<script>
  import { createEventDispatcher } from 'svelte'

  export let company

  const dispatch = createEventDispatcher()

  function dispatchTagClick(tag) {
    dispatch('tagClick', tag)
  }
</script>

<article class="group relative bg-surface-900 border border-surface-800 rounded-xl transition-all duration-300 hover:border-surface-700 hover:shadow-lg hover:shadow-accent-500/5 h-full flex flex-col">
  <!-- Top accent line on hover -->
  <div class="absolute top-0 left-0 right-0 h-0.5 bg-accent-500 scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left rounded-t-xl"></div>

  <div class="p-5 flex flex-col h-full">
    <!-- Header badges -->
    <div class="flex items-start justify-between gap-3 mb-3 shrink-0">
      <div class="flex items-center gap-2 flex-wrap">
        {#each company.origin as o}
          <span class="inline-flex items-center px-2 py-0.5 rounded-md bg-accent-500/10 text-accent-400 text-[11px] font-semibold uppercase tracking-wider border border-accent-500/20">
            {o}
          </span>
        {/each}
        {#each company.company_type as t}
          <span class="inline-flex items-center px-2 py-0.5 rounded-md bg-surface-700 text-surface-300 text-[11px] font-semibold uppercase tracking-wider border border-surface-600">
            {t}
          </span>
        {/each}
      </div>
      <span class="inline-flex items-center px-2 py-0.5 rounded-md bg-surface-800 text-surface-400 text-[11px] font-medium border border-surface-700 shrink-0">
        {company.employees}
      </span>
    </div>

    <!-- Title -->
    <h2 class="text-base font-semibold text-white leading-snug mb-1 group-hover:text-accent-400 transition-colors line-clamp-2 min-h-[2.5rem]">
      {company.name}
    </h2>

    <!-- Description -->
    <p class="text-sm text-surface-400 leading-relaxed mb-4 line-clamp-3 min-h-[3.75rem]">
      {company.description}
    </p>

    <!-- Tags -->
    {#if company.tags && company.tags.length > 0}
      <div class="flex flex-wrap gap-1.5 mb-4 shrink-0 overflow-hidden h-6">
        {#each company.tags as tag}
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

    <!-- Actions -->
    <div class="flex gap-2 shrink-0">
      <a
        href={company.website_url}
        target="_blank"
        rel="noopener"
        class="w-full inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-surface-800 hover:bg-surface-700 text-surface-300 hover:text-white text-sm font-medium transition-all border border-surface-700 hover:border-surface-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
        Visit
      </a>
    </div>
  </div>
</article>
