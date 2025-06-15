<script>
    import { X } from "lucide-svelte";
    import { createEventDispatcher, onMount } from "svelte";

    let { 
        isOpen = false,
        title = "",
        showCloseButton = true,
        closeOnOverlayClick = true,
        closeOnEscape = true,
        size = "md", // sm, md, lg, xl, full
        children
    } = $props();

    const dispatch = createEventDispatcher();
    let modalElement;

    // サイズクラスのマッピング
    const sizeClasses = {
        sm: "max-w-sm",
        md: "max-w-md",
        lg: "max-w-lg",
        xl: "max-w-xl",
        "2xl": "max-w-2xl",
        full: "max-w-full mx-4"
    };

    function closeModal() {
        dispatch('close');
    }

    function handleOverlayClick(event) {
        if (closeOnOverlayClick && event.target === event.currentTarget) {
            closeModal();
        }
    }

    function handleKeydown(event) {
        if (closeOnEscape && event.key === 'Escape') {
            closeModal();
        }
    }

    onMount(() => {
        if (closeOnEscape) {
            document.addEventListener('keydown', handleKeydown);
            return () => {
                document.removeEventListener('keydown', handleKeydown);
            };
        }
    });

    // モーダルが開いているときにボディのスクロールを無効にする
    $effect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }

        return () => {
            document.body.style.overflow = '';
        };
    });
</script>

{#if isOpen}
    <!-- オーバーレイ -->
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-opacity-20 backdrop-blur-xs"
        onclick={handleOverlayClick}
        onkeydown={handleKeydown}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? "modal-title" : undefined}
        tabindex="-1"
    >
        <!-- モーダルコンテンツ -->
        <div 
            bind:this={modalElement}
            class="relative w-full {sizeClasses[size]} bg-white rounded-lg border border-gray-300 transform transition-all duration-200 ease-out max-h-[90vh] overflow-hidden"
            onclick={(e) => e.stopPropagation()}
            onkeydown={(e) => e.stopPropagation()}
            role="document"
        >
            <!-- ヘッダー -->
            {#if title || showCloseButton}
                <div class="flex items-center justify-between p-4 border-b border-gray-200">
                    {#if title}
                        <h2 id="modal-title" class="text-lg font-semibold text-gray-900">
                            {title}
                        </h2>
                    {:else}
                        <div></div>
                    {/if}
                    
                    {#if showCloseButton}
                        <button
                            type="button"
                            class="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
                            onclick={closeModal}
                            aria-label="モーダルを閉じる"
                        >
                            <X class="w-5 h-5" />
                        </button>
                    {/if}
                </div>
            {/if}

            <!-- コンテンツ -->
            <div class="overflow-y-auto max-h-[calc(90vh-8rem)]">
                {#if children}
                    {@render children()}
                {/if}
            </div>
        </div>
    </div>
{/if}

<style>
    /* アニメーション用のカスタムスタイル */
    .modal-enter {
        opacity: 0;
        transform: scale(0.95);
    }
    
    .modal-enter-active {
        opacity: 1;
        transform: scale(1);
        transition: opacity 200ms ease-out, transform 200ms ease-out;
    }
    
    .modal-leave {
        opacity: 1;
        transform: scale(1);
    }
    
    .modal-leave-active {
        opacity: 0;
        transform: scale(0.95);
        transition: opacity 150ms ease-in, transform 150ms ease-in;
    }
</style>
