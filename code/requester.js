const https = require('https');

class Requester {
    constructor(connect) {
        this.CONNECT = connect;

        const envRiotKey = process.env['RIOT-KEY'];
        if(envRiotKey) {
            this.OPTIONS = {
                headers: {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                    'X-Riot-Token': envRiotKey
                }
            };
        } else {
            this.OPTIONS = {
                headers: {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                    'X-Riot-Token': require('./credentials.js')['RIOT-KEY']
                }
            };
        }
    }

    getSummoner(name, verbose=false) {
        if(this.CONNECT) {
            return this.getUrl(`https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/${name}`, verbose);
        } else {
            return new Promise((resolve, reject) => {
                resolve({name: "TsimpleT"});
            });
        }
    }

    getUrl(url, verbose) {
        return new Promise((resolve, reject) => {
            https.get(url, this.OPTIONS, (res) => {
                // console.log('statusCode:', res.statusCode);
                // console.log('headers:', res.headers);
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    let json = JSON.parse(data);
                    if(verbose) {
                        console.log(json);
                    }
                    resolve(json);
                });
            }).on('error', err => {
                console.error(err);
                reject(err);
            });
        });
        
        
    }
};

module.exports = {
    Requester: Requester
}