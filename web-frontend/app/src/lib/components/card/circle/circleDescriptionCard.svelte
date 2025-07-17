<script>
    import { Badge } from 'flowbite-svelte';

    import { User, ChevronRight, Circle } from 'lucide-svelte';

    /** @type {{ circle: import('../../../../../sns/circles/models').Circle }} */
    let { circle } = $props();
</script>

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