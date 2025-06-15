<script>
    import { Heart, Bookmark, Ban, Siren } from 'lucide-svelte';

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let posts = [];

    for (let i = 0; i < 10; i++) {
        posts.push({
            id: i + 1,
            user: {
                pfp: `https://picsum.photos/${i + 1}00`,
                id: i + 1,
                name: "ユーザー" + (i + 1),
            },
            title: "投稿" + (i + 1),
            content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            created_at: "2025-06-09 12:00:00",
            updated_at: "2025-06-09 12:00:00",
        });
    }
</script>

<div class="flex flex-col gap-2 w-full">
    {#each posts as post}
        <div class="flex flex-col w-full bg-white rounded-lg p-2 gap-4 border border-gray-300">
            <div class="flex flex-row gap-2 items-center justify-between">
                <div class="flex flex-row gap-2 items-center">
                    <img src={post.user.pfp} alt={post.user.name} class="w-10 h-10 rounded-full object-cover" />
                    <p class="text-lg font-bold">{post.user.name}</p>
                </div>
                <div class="flex flex-row gap-2 items-center">
                    <Heart class="w-6 h-6 text-gray-500" />
                    <Bookmark class="w-6 h-6 text-gray-500" />
                    <Ban class="w-6 h-6 text-gray-500" />
                    <Siren class="w-6 h-6 text-gray-500" />
                </div>
            </div>
            <p class="text-sm text-gray-500">{post.content}</p>
        </div>
    {/each}
</div>