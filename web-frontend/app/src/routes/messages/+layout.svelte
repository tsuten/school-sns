<script>
    import { Avatar } from 'flowbite-svelte';
    import { Button } from 'flowbite-svelte';
    import { Pin } from 'lucide-svelte';

    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();

    let users = [
        {
            id: 1,
            image: 'https://picsum.photos/200',
            display_name: 'John Doe',
            username: 'john.doe',
            email: 'john.doe@example.com'
        },
        {
            id: 2,
            image: 'https://picsum.photos/100',
            display_name: 'Jane Doe',
            username: 'jane.doe',
            email: 'jane.doe@example.com'
        },
        {
            id: 3,
            image: 'https://picsum.photos/400',
            display_name: 'John Smith',
            username: 'john.smith',
            email: 'john.smith@example.com'
        },
    ];
</script>

<div class="flex flex-row gap-2 h-full w-full">
    <div class="flex flex-col gap-2 h-full w-full">
        <div class="flex flex-col gap-2">
            <p class="text-lg font-bold">検索する</p>
        </div>
        <div class="flex flex-col gap-2 border-r border-gray-300 p-2 h-full w-full">
            {#each users as user}
                <a href={`/messages/${user.id}`}>
                    <Button class="flex flex-row justify-between gap-2 border border-gray-300 hover:cursor-pointer px-2 w-full" color="light">
                        <div class="flex flex-row gap-2 items-center">
                            <Avatar src={user.image} />
                            <div class="flex flex-col justify-start items-start">
                                <p class="text-sm">{user.display_name}</p>
                                <p class="text-xs text-gray-500">@{user.username}</p>
                            </div>
                        </div>
                        <div class="flex flex-row gap-1 items-start justify-start">
                            <Pin class="w-4 h-4" />
                        </div>
                    </Button>
                </a>
            {/each}
        </div>
    </div>
    {@render children()}
</div>