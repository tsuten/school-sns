<script>
    import { datetimeNormalize } from '$lib/utils/datetimeNormalize';
    import { Clock } from 'lucide-svelte';
    import { Tooltip } from 'flowbite-svelte';

    let { date } = $props();
</script>

<div class="flex flex-row gap-1 items-center select-none">
    <Clock class="w-4 h-4" />
    <div class="flex flex-row gap-1 items-center self-end text-sm text-gray-500">
        {datetimeNormalize(date)}
    </div>
    <Tooltip class="flex flex-row items-center gap-1">
        <span>{date}</span>
    </Tooltip>
</div>