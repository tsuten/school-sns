<script>
    import { Toast } from 'flowbite-svelte';
    import { toasts, removeToast } from '$lib/stores/toast.js';
    import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-svelte';
    import { fly, fade, scale } from 'svelte/transition';
    import { quintOut, backOut } from 'svelte/easing';

    // カスタムトランジション関数
    function toastIn(node, { delay = 0, duration = 400 }) {
        return {
            delay,
            duration,
            easing: quintOut,
            css: (t) => {
                const eased = quintOut(t);
                return `
                    transform: translateY(${(1 - eased) * 50}px);
                    opacity: ${eased};
                `;
            }
        };
    }

    function toastOut(node, { delay = 0, duration = 300 }) {
        return {
            delay,
            duration,
            easing: quintOut,
            css: (t) => {
                return `
                    opacity: ${t};
                `;
            }
        };
    }

    function getIcon(type) {
        switch (type) {
            case 'success':
                return CheckCircle2;
            case 'warning':
                return AlertTriangle;
            case 'error':
                return XCircle;
            default:
                return Info;
        }
    }

    function getToastColor(type) {
        switch (type) {
            case 'success':
                return 'green';
            case 'warning':
                return 'yellow';
            case 'error':
                return 'red';
            default:
                return 'blue';
        }
    }
</script>

<div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
    {#each $toasts as toast, index (toast.id)}
        <div
            in:toastIn={{ duration: 400, delay: index * 50 }}
            out:toastOut={{ duration: 300 }}
        >
            <Toast 
                color={getToastColor(toast.type)}
                dismissable={true}
                on:close={() => removeToast(toast.id)}
                class="shadow-none rounded-sm border border-gray-300 [&_button]:hover:cursor-pointer"
            >
                {#snippet icon()}
                    <svelte:component this={getIcon(toast.type)} class="h-5 w-5" />
                    <span class="sr-only">{toast.type} icon</span>
                {/snippet}
                {toast.message}
            </Toast>
        </div>
    {/each}
</div> 