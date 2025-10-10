<script>
    import { theme } from "$lib/theme.js";
    let { children, class: className = "" } = $props();
</script>

<div class="w-full flex flex-col p-4 rounded-sm {$theme.card.background} {$theme.border.primary} {className}">
    {@render children()}
</div>