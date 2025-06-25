<script>
    import { Users, Tag, User, ChevronRight, Search, ChevronDown } from 'lucide-svelte';
    import { apiClient } from '$lib/services/django';
    import { Button, Badge, Input, Dropdown, DropdownItem } from 'flowbite-svelte';

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let circles = $state([]);

    let category = $state('カテゴリー');

    $effect(() => {
        apiClient.get('/circle/public').then((response) => {
            circles = response;
        });
    });

    // circles変数の変更を監視してコンソールに出力
    $inspect(circles);

    // カテゴリーの日本語表示マッピング
    const categoryLabels = {
        all: 'すべて',
        study: '学習',
        hobby: '趣味',
        game: 'ゲーム',
        music: '音楽',
        art: '美術',
        sports: 'スポーツ',
        other: 'その他'
    };

    function setCategory(categoryValue) {
        category = categoryLabels[categoryValue];
        console.log(category);
    }
</script>

<div class="container mx-auto p-4 flex flex-col gap-4">
    <div class="flex flex-row gap-4 w-full">
        <div class="flex flex-row justify-center">
            <Button size="xs" color="light" class="text-sm w-32 hover:cursor-pointer rounded-sm flex items-center gap-2 whitespace-nowrap overflow-hidden justify-start">
                <ChevronDown class="w-4 h-4" />
                {category}
            </Button>
            <Dropdown simple>
                {#each Object.keys(categoryLabels) as category}
                    <DropdownItem class="text-sm hover:cursor-pointer w-full" onclick={() => setCategory(category)}>{categoryLabels[category]}</DropdownItem>
                {/each}
            </Dropdown>
        </div>
        <div class="relative w-full">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <Search class="w-5 h-5 text-gray-500" />
            </div>
            <Input
                placeholder="サークルを検索..."
                class="pl-10 rounded-sm"
            />
        </div>
    </div>
    <div class="">
        <h1 class="text-2xl font-bold text-gray-800 mb-2">公開サークル</h1>
        <p class="text-gray-600">参加可能なサークルを探してみましょう</p>
    </div>

    {#if circles.length === 0}
        <div class="text-center py-12">
            <Users class="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">公開サークルが見つかりませんでした</p>
        </div>
    {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
            {#each circles as circle}
                <div class="border border-gray-300 rounded-sm p-4">
                    <!-- サークル名とカテゴリー -->
                    <div class="mb-3">
                        <h3 class="text-lg font-bold text-gray-800 mb-1">{circle.name}</h3>
                        <Badge color="blue" class="text-xs">
                            {categoryLabels[circle.category] || circle.category}
                        </Badge>
                    </div>

                    <!-- 説明文 -->
                    {#if circle.description}
                        <p class="text-gray-600 text-sm mb-3 line-clamp-2">{circle.description}</p>
                    {/if}

                    <!-- タグ -->
                    {#if circle.tags && circle.tags.length > 0}
                        <div class="flex flex-wrap gap-1 mb-3 hover">
                            {#each circle.tags.slice(0, 3) as tag}
                                <Badge color="gray" class="text-xs">
                                    {tag.name}
                                </Badge>
                            {/each}
                            {#if circle.tags.length > 3}
                                <span class="text-gray-500 text-xs">+{circle.tags.length - 3}個</span>
                            {/if}
                        </div>
                    {/if}

                    <!-- 作成者情報 -->
                    <div class="flex items-center justify-between pt-3 border-t border-gray-200">
                        <div class="flex items-center gap-1">
                            <User class="w-4 h-4 text-gray-500" />
                            <span class="text-sm text-gray-600">{circle.founder?.username || '不明'}</span>
                            <span class="text-xs text-gray-600">+ {circle.members?.length || '0'} メンバー</span>
                        </div>
                        <a href={`/circles/${circle.id}`}>
                            <Button size="xs" color="blue" class="text-sm hover:cursor-pointer flex items-center gap-2 rounded-sm">
                                詳しく
                                <ChevronRight class="w-4 h-4" />
                            </Button>
                        </a>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>