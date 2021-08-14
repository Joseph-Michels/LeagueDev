const express = require('express');
const ejs = require('ejs');

class TestRouter {
    constructor(database, verbose=false) {
        this.VERBOSE = verbose;

        this.router = express.Router();

        this.router.get("/liveGame/:username", async (req, res) => {
            let name = req.params.username;
            let summoner = await database.getSummonerByName(name);
            let liveGame = await database.getLiveGameBySummonerId(summoner.id);

            res.send(liveGame);
        
            // let objects = {
            //     summonerName: name,
            //     summonerLevel: summoner.summonerLevel,
            //     iconId: summoner.profileIconId,
            //     test: 'summoner name from firestore',
            //     test_array: [],
            //     groupNames: groupDict.names,
            //     groupIds: groupDict.ids
            // }
        
            // res.send(await ejs.renderFile('views/pages/index.ejs', objects, {async: true}));
        })
    }
}

module.exports = TestRouter;