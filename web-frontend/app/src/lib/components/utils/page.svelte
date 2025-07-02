<script>
    let { children } = $props();
</script>

<div class="flex flex-col gap-4 p-4">
    {@render children()}
</div>