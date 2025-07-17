<script>
    let { logo, title, subtitle, children } = $props();
</script>

<div class="flex flex-row items-center justify-between gap-3 px-4 py-2 border-b border-gray-200 bg-white">
    <div class="flex flex-row items-center gap-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden">
            <img src={logo} alt={title} class="w-full h-full object-cover" />
        </div>
        <div class="flex flex-col">
            <h1 class="text-2xl font-bold">{title}</h1>
            <p class="text-sm text-gray-500">{subtitle}</p>
        </div>
    </div>
    {@render children()}
</div>