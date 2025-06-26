<script>
    /** @type {{ user: import('../../types').User }} */
    let { user } = $props();
</script>

<div>
    <h1>{user.display_name}</h1>
</div>