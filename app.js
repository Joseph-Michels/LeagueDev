// node_modules imports
const express = require('express');
const ejs = require('ejs');
const favicon = require('serve-favicon');

// other file imports
const Database = require('./code/database');

// node_modules initialization
const app = express();
app.set('view engine', 'ejs');
app.use(favicon(__dirname + '/public/images/favicon.ico'));

const PORT = process.env.PORT || 3000;

// other files initialization
const database = new Database();

/*
liveGames: [
    // {
    //     start: "23:45",
    //     mode1: "Ranked",
    //     mode2: "S/D",
    //     names: ["TsimpleT", "Tzuyu Fanboy"]
    // },
    // {
    //     start: "34:56",
    //     mode1: "Normal",
    //     mode2: "Draft",
    //     names: ["SpikyBuffalo", "vFirePat"]
    // }
]
*/


app.listen(PORT, (err) => {
    if(err) {
        console.log("ERROR in app.listen:");
        console.log(err);
    } else {
        console.log(`Server running on port ${PORT}`);
    }
});

app.get("/", async (req, res) => {
    let name = (await database.firestore.getTestSummonerName()).testkey;
    let summoner = await database.getSummonerByName(name, true);
    let groupDict = (await database.firestore.getGroups());

    let objects = {
        summonerName: name,
        summonerLevel: summoner.summonerLevel,
        iconId: summoner.profileIconId,
        liveGames: [],
        test: 'summoner name from firestore',
        test_array: [],
        groupNames: groupDict.names,
        groupIds: groupDict.ids
    }

    res.send(await ejs.renderFile('views/pages/index.ejs', objects, {async: true}));
});

app.get("/:username", async (req, res) => {
    let name = req.params.username;
    let summoner = (await database.getSummonerByName(name));
    let groupDict = (await database.firestore.getGroups());
    let objects = {
        summonerName: name,
        summonerLevel: summoner.summonerLevel,
        iconId: summoner.profileIconId,
        liveGames: [],
        test: 'from url',
        test_array: [],
        groupNames: groupDict.names,
        groupIds: groupDict.ids
    }

    res.send(await ejs.renderFile('views/pages/index.ejs', objects, {async: true}));
});

// app.get("/favicon.ico", (req, res) => {
//     res.status(204).end();
// });

app.get("/group/:groupId", async (req, res) => {
    res.redirect(`/group/${req.params.groupId}/leaderboard`);
});

app.get("/group/:groupId/leaderboard", async (req, res) => {
    let group = await database.firestore.getGroup(req.params.groupId);
    let summoners = [];

    for(let i = 0; i < group.ids.length; i++) {
        let summoner = await database.getSummonerById(group.ids[i]);
        summoners.push(summoner);
    }

    let objects = {
        liveGames: [],
        summoners: summoners
    };

    res.send(await ejs.renderFile('views/pages/groupLeaderboard.ejs', objects, {async: true}));
});



