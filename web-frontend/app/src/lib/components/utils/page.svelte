<script>
    let { children, class: className = "" } = $props();
</script>

<div class="flex flex-col gap-4 p-4 h-full overflow-y-auto {className}">
    {@render children()}
</div>