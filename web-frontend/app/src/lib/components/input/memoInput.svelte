<script>
    import { onMount } from 'svelte';
    import { apiClient } from '$lib/services/django';
    import { Input } from 'flowbite-svelte';
</script>

<div class="flex flex-col gap-4">
    <Input type="text" placeholder="メモを入力" />
</div>