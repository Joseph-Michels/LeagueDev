/***************************************************************************
 | IMPORTS                                                                 |
 ***************************************************************************/
const express = require('express');
const favicon = require('serve-favicon');

const Database = require('./database/database');
const MainRouter = require('./routers/mainRouter');
const GroupRouter = require('./routers/groupRouter');

/***************************************************************************
 | INIT                                                                    |
 ***************************************************************************/
const app = express();
app.set('view engine', 'ejs');
app.use(favicon(__dirname + '/../public/images/favicon.ico'));

const database = new Database(useDummyResponses=false, verbose=false);
const mainRouter = new MainRouter(database, verbose=false).router;
const groupRouter = new GroupRouter(database, verbose=false).router;

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

app.use('/', mainRouter);
app.use('/group', groupRouter);