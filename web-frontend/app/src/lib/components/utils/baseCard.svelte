<script>
    let { children, class: className = "" } = $props();
</script>

<div class="flex flex-col bg-white p-4 rounded-sm border border-gray-300 {className}">
    {@render children()}
</div>