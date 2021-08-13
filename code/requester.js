const https = require('https');

class Requester {
    constructor() {
        this.OPTIONS = {
            headers: {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                'X-Riot-Token': process.env['RIOT-KEY']
            }
        };

        if(!this.OPTIONS.headers['X-Riot-Token']) {
            this.OPTIONS.headers['X-Riot-Token'] = require('./credentials.js')['RIOT-KEY'];
        }
    }

    async getSummonerById(id, verbose) {
        return this.getUrl(`https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${id}`, verbose);  
    }

    async getSummonerByName(name, verbose) {
        return this.getUrl(`https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/${name}`, verbose);  
    }

    getUrl(url, verbose) {
        return new Promise((resolve, reject) => {
            https.get(url, this.OPTIONS, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    let json = JSON.parse(data);
                    if(verbose) {
                        console.log('-------------------------------------------------------------------------------------------------------');
                        console.log(url);
                        console.log('statusCode:', res.statusCode);
                        console.log('headers:', this.updateRateLimitsFromHeader(res.headers));
                        console.log('output:', json);
                    }
                    
                    resolve(json);
                });
            }).on('error', err => {
                console.error(err);
                reject(err);
            });
        });
    }

    updateRateLimitsFromHeader(header) {
        let dict = {'app': {}, 'method': {}};

        // app
        let appLimit = header['x-app-rate-limit'].split(',');
        let appCount = header['x-app-rate-limit-count'].split(',');
        for(let i = 0; i < appLimit.length; i++) {
            let countIdx = appCount[i].indexOf(':');
            let count = appCount[i].substr(0, countIdx);
            let limit = appLimit[i].substr(0, appLimit[i].indexOf(':'));
            let size = appCount[i].substr(countIdx+1);
            console.log(`${count}/${limit} in ${size}s`);
            dict.app[size] = limit - count;
        }

        // method
        let methodLimit = header['x-method-rate-limit'].split(',');
        let methodCount = header['x-method-rate-limit-count'].split(',');
        for(let i = 0; i < methodLimit.length; i++) {
            let countIdx = methodCount[i].indexOf(':');
            let count = methodCount[i].substr(0, countIdx);
            let limit = methodLimit[i].substr(0, methodLimit[i].indexOf(':'));
            let size = methodCount[i].substr(countIdx+1);
            console.log(`${count}/${limit} in ${size}s`);
            dict.method[size] = limit - count;
        }

        return dict;
    }
};

module.exports = Requester;