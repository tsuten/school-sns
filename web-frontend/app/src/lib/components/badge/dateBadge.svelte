<script>
    import { dateNormalize } from '$lib/utils/datetimeNormalize';
    import { Clock } from 'lucide-svelte';
    import { Tooltip } from 'flowbite-svelte';
    let { date, showClock = true } = $props();
</script>

<div class="flex flex-row gap-1 items-center select-none">
    {#if showClock}
        <Clock class="w-4 h-4" />
    {/if}
    <div class="flex flex-row gap-1 items-center self-end text-sm text-gray-500">
        {dateNormalize(date)}
    </div>
    <Tooltip class="flex flex-row items-center gap-1">
        <span>{date}</span>
    </Tooltip>
</div>