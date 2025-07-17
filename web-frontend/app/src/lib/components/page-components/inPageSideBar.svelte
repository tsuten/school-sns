<script>
    import { Crown, Hash, Users } from 'lucide-svelte';
    let { children, hoverWidth = 80 } = $props();
</script>

<div class="w-16 hover:w-{hoverWidth} border-r border-gray-300 flex flex-col transition-all duration-300 ease-in-out group">
    <!-- サークル一覧 -->
    <div class="flex-1 overflow-y-auto">
        {@render children()}
    </div>
</div>