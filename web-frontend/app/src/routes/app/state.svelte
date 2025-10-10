<script>
	import { activeWidgets } from '$lib/stores/widgets';
    let widgets = [];

    function addWidget() {
        activeWidgets.set([...$activeWidgets, "widget"]);
    }

    function removeWidget() {
        activeWidgets.set($activeWidgets.slice(0, -1));
    }
</script>

<div class="flex flex-col gap-2 w-full">
	<div class="flex flex-col gap-2 w-full">
		<p>Active Widgets</p>
		<ul class="flex flex-row gap-2">
			{#each $activeWidgets as widget}
				<li class="border border-gray-300 rounded-lg p-2 w-full">{widget}</li>
			{/each}
		</ul>
	</div>
    <button class="border border-gray-300 rounded-lg p-2 w-full hover:cursor-pointer" onclick={addWidget}>
        <p>Add Widget</p>
    </button>
    <button class="border border-gray-300 rounded-lg p-2 w-full hover:cursor-pointer" onclick={removeWidget}>
        <p>Remove Widget</p>
    </button>
</div>