<script>
    import { apiClient } from "$lib/services/django";
    import { page } from "$app/stores";
    import { onMount } from "svelte";

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let members = $state([]);

    onMount(async () => {
        const response = await apiClient.get(`/enrollments/members/${$page.params.class}`);
        members = response;
    });
</script>

{#each members as member}
    <div>
        <h1>{member.display_name}</h1>
    </div>
{/each}