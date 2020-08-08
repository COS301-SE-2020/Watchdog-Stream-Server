const io = require("socket.io-client"),
    ioClient = io.connect("http://127.0.0.1:8008");

var msg;

ioClient.emit("authorize",
    { 
        "user_id" : "dcdaeb64-e23f-46d1-84f7-dd8d1f1a8847",
        "client_type" : "consumer",
        "client_key" : "string"
    }
);

ioClient.emit("consume-view",
    {
        "camera_list" : ["c91be10abd48462a5a606df692bdcfbd3ab8860802e70328f79b08232ec638cc1"]
    }
);

ioClient.on("consume-frame", 
    (message) => console.log(message)
);
