<script>
    let { children } = $props();
</script>

<div class="border border-gray-300 rounded-sm p-4 w-full">
    {@render children()}
</div>