<script>
    import { User } from "lucide-svelte";

    let { 
        username = "user123",
        displayName = "ユーザー名",
        avatarUrl = null,
        size = "md", // sm, md, lg
        showUsername = true,
        showDisplayName = true,
        layout = "horizontal" // horizontal, vertical
    } = $props();

    // サイズクラスのマッピング
    const sizeClasses = {
        sm: {
            avatar: "w-8 h-8",
            icon: "w-4 h-4",
            username: "text-xs",
            displayName: "text-sm font-medium"
        },
        md: {
            avatar: "w-10 h-10",
            icon: "w-5 h-5",
            username: "text-sm",
            displayName: "text-base font-medium"
        },
        lg: {
            avatar: "w-12 h-12",
            icon: "w-6 h-6",
            username: "text-base",
            displayName: "text-lg font-medium"
        }
    };

    const currentSize = sizeClasses[size];
    const layoutClass = layout === "vertical" ? "flex-col items-center text-center" : "flex-row items-center";
</script>

<div class="flex {layoutClass} gap-2">
    <!-- アバター/アイコン -->
    <div class="flex-shrink-0">
        {#if avatarUrl}
            <img 
                src={avatarUrl} 
                alt="{displayName}のアバター"
                class="{currentSize.avatar} rounded-full object-cover border border-gray-200"
            >
        {:else}
            <div class="{currentSize.avatar} rounded-full bg-gray-100 flex items-center justify-center border border-gray-200">
                <User class="{currentSize.icon} text-gray-500" />
            </div>
        {/if}
    </div>

    <!-- ユーザー情報 -->
    {#if showDisplayName || showUsername}
        <div class="flex flex-col {layout === 'vertical' ? 'items-center' : 'items-start'} min-w-0">
            {#if showDisplayName}
                <p class="{currentSize.displayName} text-gray-900 truncate">
                    {displayName}
                </p>
            {/if}
            {#if showUsername}
                <p class="{currentSize.username} text-gray-500 truncate">
                    @{username}
                </p>
            {/if}
        </div>
    {/if}
</div>
