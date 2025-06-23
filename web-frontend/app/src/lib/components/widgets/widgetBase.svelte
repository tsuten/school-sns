<script>
    let { icon, title, snippet, href } = $props();
    import { ChevronRight } from 'lucide-svelte';
</script>

<div class="border border-gray-300 rounded-lg p-4 w-full">
    <div class="flex flex-row justify-between gap-1 items-center">
        <div class="flex items-center justify-center gap-1">
            <svelte:component this={icon} class="w-6 h-6 text-gray-500" />
            <h2 class="text-gray-500 text-lg font-bold">{title}</h2>
        </div>
        <a href={href} class="text-gray-500 text-sm font-bold text-center flex items-center gap-1 hover:cursor-pointer">
            <span>もっと</span>
            <ChevronRight class="w-4 h-4" />
        </a>
    </div>
    <div class="flex flex-col gap-1 items-center w-full pt-2">
        {#if snippet}
            {@render snippet()}
        {/if}
    </div>
</div>