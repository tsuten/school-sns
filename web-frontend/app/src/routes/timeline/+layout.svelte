<script>
    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();
</script>

<div class="flex flex-col gap-2 h-full">
    <div class="flex flex-row gap-2 border-b border-gray-300 p-2 items-center justify-around">
        <button class="text-lg font-bold hover:cursor-pointer hover:bg-gray-200 rounded-sm p-2 w-full">タイムライン</button>
        <button class="text-lg font-bold hover:cursor-pointer hover:bg-gray-200 rounded-sm p-2 w-full">最新の投稿</button>
        <button class="text-lg font-bold hover:cursor-pointer hover:bg-gray-200 rounded-sm p-2 w-full">最近の投稿</button> 
    </div>
    <div class="flex flex-row gap-2 p-4 overflow-y-auto h-full">
        {@render children()}
    </div>
</div>