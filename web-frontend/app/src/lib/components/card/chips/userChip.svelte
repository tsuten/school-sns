<script>
    import { User } from "lucide-svelte";
    import { theme } from "$lib/theme.js";
    let { user } = $props();
</script>

<div class="flex flex-row gap-2 items-center hover:cursor-pointer rounded-sm p-1 select-none text-sm {$theme.text.tertiary} hover:{$theme.button.secondary}">
    <User class="w-4 h-4 {$theme.text.tertiary}" />
    <p class="{$theme.text.tertiary}">{user}</p>
</div>