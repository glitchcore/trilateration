
const fs = require('fs');
const http = require('http');

// min and max values for X and Y
const minX = 0;
const maxX = 2.8;
const minY = 0;
const maxY = 4.9;

index = fs.readFileSync(__dirname + '/index.html');

/* // Adding three beacons SECOND SETTING
trilateration.addBeacon(2, trilateration.vector(0, 7.9));
trilateration.addBeacon(0, trilateration.vector(3.97, 9.85));
trilateration.addBeacon(1, trilateration.vector(6.47, 7.9)); */


function correct_position(pos, minX, maxX, minY, maxY) {
    if (pos.x < minX) pos.x = minX;
    if (pos.x > maxX) pos.x = maxX;
    if (pos.y < minY) pos.y = minY;
    if (pos.y > maxY) pos.y = maxY;

    return pos;
}

const A = 0.7162624467;
const B = 8.195495665;
const C = 0.0894828774;
const REF_RSSI = -59;

function rssi2distance(rssi) {
    let ratio = rssi / REF_RSSI;

    return A * Math.pow(ratio, B) + C;
}

function payload_parse(payload) {
    // console.log("payload length:", payload.length);

    let pos = 0;

    let id = payload.readUInt32BE(pos).toString(16); // {8 bytes of ID}
    pos += 4;

    id += payload.readUInt32BE(pos).toString(16); // {8 bytes of ID}
    pos += 4;

    let lon = payload.readFloatLE(pos); // {4 byte of lon - iEEE 754 float}
    pos += 4;

    let lat = payload.readFloatLE(pos); // {4 byte of lat - iEEE 754 float}
    pos += 4;

    let alt = payload.readFloatLE(pos); // // {4 byte of alt - iEEE 754 float}
    pos += 4;

    /// {1 byte of cmd type}
    // 0x01 - Send a distress signal
    // 0x02 - Cancel an accident
    // 0x03 - Track sportsman
    let cmd = payload.readUInt8(pos);
    pos += 1;

    let ts = new Date(payload.readUInt32LE(pos) * 1e3).toISOString();  // {4 bytes - UNIX timestamp}
    pos += 4;

    ble_location = [];

    let ble_size = payload.readUInt8(pos);
    pos += 1;

    // console.log("ble size:", ble_size);

    for(let i = 0; i < ble_size; i++) {
        let mac = [];
        mac.push(payload.readUInt8(pos).toString(16));
        pos += 1;
        mac.push(payload.readUInt8(pos).toString(16));
        pos += 1;
        mac.push(payload.readUInt8(pos).toString(16));
        pos += 1;

        mac = mac.reverse().join(":");

        let rssi = payload.readInt8(pos);
        pos += 1;

        // console.log("rssi:", rssi);

        ble_location.push({
            mac: mac.toString(16),
            rssi
        });
    }

    return {
        id,
        lon,
        lat,
        alt,
        cmd,
        ts,
        ble_location
    };
}

const AVERAGE_COUNT = 5;

var beacon_list = [
    {
        id: "a4:a8",
        pos: [0.1, 0.1],
        rssi: []
    },
    {
        id: "aa:69",
        pos: [2.4, 4.8],
        rssi: []
    },
    {
        id: "d9:ab",
        pos: [0.1, 4.8],
        rssi: []
    },
    {
        id: "95:51",
        pos: [2.7, 0.7],
        rssi: []
    }
];

const port = 8085;

let server = http.createServer(
    (req, res) => {
        // console.log(`Request: ${req.method} URL: ${req.url}`)

        if (req.method == 'POST') {
            let body = [];
            req.on('data', (chunk) => {
                body.push(chunk);
            }).on('end', () => {
                // console.log("get data", Buffer.concat(body).toString());

                body = JSON.parse(Buffer.concat(body).toString());

                // console.log("raw b64 data:", body.data);
                let payload = new Buffer.from(body.data, 'base64');
                // console.log(JSON.stringify(payload_parse(payload)));

                // console.log("raw b64 data:", body.data);
                let message = payload_parse(payload);

                let ts_diff = (new Date() - new Date(message.ts))/1000;

                
                console.log(`\
[${new Date().toISOString().substring(11, 19)}] ${message.id} \
lat:${message.lat.toFixed(3)}, lon:${message.lon.toFixed(3)},\
ts:${message.ts}`);

                let trilateration = require('./node_modules/trilateration/index.js');

                message.ble_location.forEach(item => {
                    let mac = item.mac.split(":").slice(1,3).join(":");

                    let distance = rssi2distance(item.rssi);
                    console.log(`${mac} ${item.rssi} ${distance.toFixed(3)} m`);

                    // get beacon id
                    let a = beacon_list
                        .map((x,i) => [x,i])
                        /*.map(x => {
                            console.log(x);
                            return x;
                        })*/
                        .filter(x => x[0].id === mac);

                    // console.log(a);

                    if(a.length != 1){
                        console.error("wrong beacon", a);
                        return;
                    }

                    let beacon_id = a[0][1];

                    // console.log("get beacon", beacon_id);

                    trilateration.addBeacon(
                        beacon_id,
                        trilateration.vector(
                            beacon_list[beacon_id].pos[0],
                            beacon_list[beacon_id].pos[1]
                        )
                    );

                    if(distance < Math.sqrt(maxX * maxX + maxY * maxY)) {
                        beacon_list[beacon_id].rssi.push(item.rssi);
                        if(beacon_list[beacon_id].rssi.length > AVERAGE_COUNT) {
                            beacon_list[beacon_id].rssi.splice(0, 1);
                        }
                    }

                    

                    let average_rssi = beacon_list[beacon_id].rssi.reduce((a,b) => a + b, 0) / beacon_list[beacon_id].rssi.length;

                    let average_distance = rssi2distance(average_rssi);

                    console.log("rssis:", beacon_list[beacon_id].rssi, "avg rssi:", average_rssi, "avg distance:", average_distance);

                    trilateration.setDistance(beacon_id, average_distance);
                });

                let pos = trilateration.calculatePosition();
                pos = correct_position(pos, minX, maxX, minY, maxY);

                console.log("X: " + pos.x + "; Y: " + pos.y);

                io.emit('coordinate', [[pos.x + Math.random()*0.05, pos.y + Math.random()*0.05, message.id]]);

                res.end();
            });
        } else {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(index);
        }
    }
);

server.listen(port, (err) => {
    if (err) {
        return console.log('something bad happened', err);
    }
    console.log(`server is listening on ${port}`);
})

let io = require('socket.io').listen(server);

io.on("connection", (socket) => {
    console.log("start connect");
    io.emit("beacon_list", beacon_list.map(item => item.pos));
});
