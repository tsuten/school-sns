<script>
    import { apiClient } from "$lib/services/django";
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    import SimpleUserProfile from "$lib/components/card/simpleUserProfile.svelte";
    import Page from "$lib/components/utils/page.svelte";
    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let members = $state([]);

    onMount(async () => {
        const response = await apiClient.get(`/enrollments/members/${$page.params.class}`);
        members = response;
    });
</script>

<Page>
    <h1 class="text-2xl font-bold">メンバー</h1>
    <div class="grid grid-cols-3 gap-4">
    {#each members as member}
        <SimpleUserProfile user={member} />
        {/each}
    </div>
</Page>