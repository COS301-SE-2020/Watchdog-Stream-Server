start python .\stream_server\client consumer USERID - PRODID1 CAM1 - PRODID2 CAMX CAMY
start python .\stream_server\client producer USERID PRODID1 CAM1 CAM2
start python .\stream_server\client producer USERID PRODID2 CAMX CAMY
start python .\stream_server\client consumer USERID - PRODID2 CAMX
start python .\stream_server\client producer USERID PRODID3 CAMV CAxY
start python .\stream_server\client consumer USERID - PRODID2 CAxY
start python .\stream_server\client consumer Uxxx - PRODID2 CAxY
start python .\stream_server\client producer Uxxx PRODID2 CAMV CAxY
