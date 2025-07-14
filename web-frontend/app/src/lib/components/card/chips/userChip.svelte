<script>
    import { User } from "lucide-svelte";
    let { user } = $props();
</script>

<div class="flex flex-row gap-2 items-center hover:cursor-pointer hover:bg-gray-100 rounded-sm p-1 select-none">
    <User class="w-4 h-4" />
    <p>{user}</p>
</div>