<script>
    import { page } from "$app/stores";
    import { apiClient } from "$lib/services/django";
    import { onMount } from "svelte";
    import Page from "$lib/components/utils/page.svelte";

    let classInfo = $state({});

    onMount(async () => {
        const response = await apiClient.get(`/enrollments/class_info/${$page.params.class}`);
        classInfo = response
    });
</script>

<Page>
    <h1>{classInfo.name}</h1>
</Page>