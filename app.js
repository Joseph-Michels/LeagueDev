// node_modules imports
const express = require('express');
const ejs = require('ejs');

// other file imports
const Requester = require('./code/requester');
const Database = require('./code/database');

// node_modules initialization
const app = express();
app.set('view engine', 'ejs');

const PORT = process.env.PORT || 3000;

// other files initialization
const requester = new Requester(true);
const database = new Database();


// tests
const baseObjects = {
    test: "From Firestore Database",
    test_array: [
        // "test1", "test2", "test3"
    ],
    live_games: [
        {
            start: "23:45",
            mode1: "Ranked",
            mode2: "S/D",
            names: ["TsimpleT", "Tzuyu Fanboy"]
        },
        {
            start: "34:56",
            mode1: "Normal",
            mode2: "Draft",
            names: ["SpikyBuffalo", "vFirePat"]
        }
    ]
};



app.listen(PORT, (err) => {
    if(err) {
        console.log("ERROR in app.listen:");
        console.log(err);
    } else {
        console.log(`Server running on port ${PORT}`);
    }
});

app.get("/", async (req, res) => {
    let objects = JSON.parse(JSON.stringify(baseObjects));

    objects.summonerName = (await database.getSummonerName()).testkey;
    objects.summonerLevel = (await requester.getSummoner(objects.summonerName)).summonerLevel;

    // console.log(objects);

    res.send(await ejs.renderFile('views/pages/index.ejs', objects, {async: true}));
});

app.get("/:username", async (req, res) => {
    let objects = {
        summonerName: req.params.username,
        summonerLevel: (await requester.getSummoner(req.params.username)).summonerLevel,
        live_games: [],
        test: '',
        test_array: []
    }
    // console.log(objects);

    res.send(await ejs.renderFile('views/pages/index.ejs', objects, {async: true}));
});