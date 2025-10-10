<script>
    import { onMount } from 'svelte';
    import { apiClient } from '$lib/services/django';
    import Announcement from '$lib/components/card/announcement/announcement.svelte';
    import Page from '$lib/components/utils/page.svelte';
    import PollCard from '$lib/components/card/pollCard.svelte';
    import { Dropdown, DropdownItem } from 'flowbite-svelte';
    /** @type {import('./$types').PageProps} */
    let { data } = $props();

    let announcements = $state([]);
    let polls = $state([]);

    onMount(async () => {
        const response = await apiClient.get('/feed/');
        const polls_response = await apiClient.get('/polls/');
        announcements = response.data;
        polls = polls_response;
    });
</script>

<Page>
    <div class="flex flex-col gap-4 max-w-4xl mx-auto">
        <h1 class="text-2xl font-bold">フィード</h1>
        <div class="flex flex-row gap-2">
            <Dropdown simple>
                <DropdownItem>
                    範囲を変更
                </DropdownItem>
            </Dropdown>
        </div>
        {#each announcements as announcement}
            <Announcement {announcement} />
        {/each}
        {#each polls as poll}
            <PollCard {poll} />
        {/each}
    </div>
</Page>