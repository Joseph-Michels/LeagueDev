const https = require('https');
const fs = require('fs');

// 'Accept', 'Content-Type', 'User-Agent' ???
const OPTIONS = {
    headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        'X-Riot-Token': ''
    }
};

fs.readFile('./credentials/riot_key.txt', "utf8", (err,data) => {
    if(err) {
        console.log("/credentials/riot_key.txt NOT FOUND");
        throw err;
    } else {
        OPTIONS.headers['X-Riot-Token'] = data;
    }
});

class Requester {
    constructor() {

    }

    getStatus() {
        console.log(OPTIONS);
        https.get(`https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/TsimpleT`, OPTIONS, (res) => {
            // console.log('statusCode:', res.statusCode);
            // console.log('headers:', res.headers);
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                console.log(JSON.parse(data));
            });
        }).on('error', (e) => {
            console.error(e);
        });
    }
};

module.exports = {
    Requester: Requester
}