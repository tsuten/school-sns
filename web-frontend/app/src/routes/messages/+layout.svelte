<script>
    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();
</script>

<div class="flex flex-col gap-2">
    <div class="flex flex-row gap-2">
        <div class="flex flex-col gap-2">
            <p class="text-lg font-bold">メッセージ</p>
        </div>
    </div>
    {@render children()}
</div>