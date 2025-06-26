<script>
    /** @type {{ user={ Display name:string , Pfp:string , Bio:string , Birthday:date , Location:string , Birth place:string} }} */
    let { user } = $props();

</script>

<div>
    <h1>{user.display_name}</h1>
    <img src="images/{user.Pfp}" alt="Dinosaur" />
    <!-- srcのimagesのところはちゃんとしたのに後で変える -->
    <p>{user.Bio}</p>
    <p>{user.Birthday}</p>
    <p>{user.Location}</p>
    <p>{user.Birth_place}</p>
    <!--  -->
</div>