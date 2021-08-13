const express = require('express');
const ejs = require('ejs');

class MainRouter {
    constructor(database, verbose=false) {
        this.VERBOSE = verbose;

        this.router = express.Router();

        this.router.get("/", async (req, res) => {
            let name = (await database.firestore.getTestSummonerName()).testkey;
            let summoner = await database.getSummonerByName(name);
            let groupDict = (await database.firestore.getGroups());
        
            let objects = {
                summonerName: name,
                summonerLevel: summoner.summonerLevel,
                iconId: summoner.profileIconId,
                test: 'summoner name from firestore',
                test_array: [],
                groupNames: groupDict.names,
                groupIds: groupDict.ids
            }
        
            res.send(await ejs.renderFile('views/pages/index.ejs', objects, {async: true}));
        });
        
        this.router.get("/:username", async (req, res) => {
            let name = req.params.username;
            let summoner = (await database.getSummonerByName(name));
            let groupDict = (await database.firestore.getGroups());
            let objects = {
                summonerName: name,
                summonerLevel: summoner.summonerLevel,
                iconId: summoner.profileIconId,
                test: 'from url',
                test_array: [],
                groupNames: groupDict.names,
                groupIds: groupDict.ids
            }
        
            res.send(await ejs.renderFile('views/pages/index.ejs', objects, {async: true}));
        });
    }
}

module.exports = MainRouter;