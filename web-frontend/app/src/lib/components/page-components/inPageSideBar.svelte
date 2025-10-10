<script>
    import { Crown, Hash, Users } from 'lucide-svelte';
    let { children, is_fixed = false } = $props();
</script>

<div class="{is_fixed ? 'w-80' : 'w-16 hover:w-80'} border-r border-gray-300 flex flex-col transition-all duration-300 ease-in-out group">
    <div class="flex-1 overflow-y-auto">
        {@render children()}
    </div>
</div>