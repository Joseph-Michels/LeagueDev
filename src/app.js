/***************************************************************************
 | IMPORTS                                                                 |
 ***************************************************************************/
const express = require('express');
const favicon = require('serve-favicon');

const Database = require('./database/database');
const SearchRouter = require('./routers/searchRouter');
const GroupRouter = require('./routers/groupRouter');
const HomeRouter = require('./routers/homeRouter');
// const TestRouter = require('./routers/testRouter');

/***************************************************************************
 | INIT                                                                    |
 ***************************************************************************/
const app = express();
app.set('view engine', 'ejs');
app.use(favicon(__dirname + '/../public/img/favicon.ico'));
app.use('/img', express.static(__dirname + '/../public/img'));

const database = new Database(useDummyResponses=false, verbose=true);
const searchRouter = new SearchRouter(database, verbose=false).router;
const groupRouter = new GroupRouter(database, verbose=false).router;
const homeRouter = new HomeRouter(database, verbose=false).router;
// const testRouter = new TestRouter(database, verbose=false).router;

/***************************************************************************
 | ROUTING                                                                 |
 ***************************************************************************/
// app.get("/favicon.ico", (req, res) => {
//     res.status(204).end();
// });

const PORT = process.env.PORT || 3000;
app.listen(PORT, (err) => {
    if(err) {
        console.log("ERROR in app.listen:");
        console.log(err);
    } else {
        console.log(`Server running on port ${PORT}`);
    }
});

app.use("/", homeRouter);
app.use('/search', searchRouter);
app.use('/group', groupRouter);
// app.use('/test', testRouter);