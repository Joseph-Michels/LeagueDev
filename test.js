function test() {
	var resource = new XMLHttpRequest();
	resource.onreadystatechange = function() {
        if(resource.readyState == 4 && resource.status == 200) {
			var data = JSON.parse(resource.responseText);
            console.log(data);
        }
	}
	resource.open("GET", "https://na1.api.riotgames.com/lol/status/v3/shard-data", true);
	resource.setRequestHeader('X-Riot-Token', config.riotKey);
	resource.setRequestHeader('Access-Control-Allow-Origin', '*');
    resource.send();
}