
From http://www.bicing.cat we can get the bikes availability:
https://www.bicing.cat/CallWebService/StationBussinesStatus_Cache.php

$ curl -d "idStation=2" https://www.bicing.cat/CallWebService/StationBussinesStatus_Cache.php -k

From http://www.citybik.es/ we can get the bikes availability:

$ curl http://api.citybik.es/bicing.json

Android app to display bike shared network status:
https://github.com/eskerda/CityBikes

82 - Rocafort
84 - Diputació
111 - Calabria
81 - Vilamarí
93 - Gran Via
94 - Gran Via
95 - Tarragona
112 - Floridablanca

SELECT * FROM RackStatus where id in (82, 84, 111, 81, 93, 94, 95, 112) order by timestamp desc