<script>
	let { icon, href, label } = $props();
</script>

<a href={href} class="flex flex-row items-center w-40 justify-end gap-2 group"> <p class="text-sm text-gray-500">{label}</p>
    <div class="w-13 h-13 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
        <svelte:component this={icon} />
    </div>
</a>