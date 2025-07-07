<script>
    let { children } = $props();
</script>

<div class="flex flex-col bg-white p-4 rounded-sm border border-gray-300">
    {@render children()}
</div>