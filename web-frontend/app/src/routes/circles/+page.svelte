<script>
    import { apiClient } from '$lib/services/django';
    import { Badge } from 'flowbite-svelte';

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let joinedCircles = $state([]);

    $inspect(joinedCircles);

    $effect(() => {
        fetchJoinedCircles();
    });

    async function fetchJoinedCircles() {
        const response = await apiClient.get(`/circle/you`);
        joinedCircles = response;
    }
</script>

<div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold">サークル一覧</h1>

    {#each joinedCircles as circle}
        <div class="bg-white rounded-sm border border-gray-300 p-4 mb-4">
            <a href="/circles/{circle.id}">
                <h2 class="text-xl font-bold">{circle.name}</h2>
            </a>
            <p class="text-gray-600">{circle.description}</p>
            {#each circle.tags as tag}
                <Badge color="blue" class="text-xs">{tag.name}</Badge>
            {/each}
            <p class="text-gray-600">{circle.members.length} メンバー</p>
            <p class="text-gray-600">{circle.created_at}</p>
        </div>
    {/each}
</div>