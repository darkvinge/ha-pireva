# ha-pireva
Pireva integration för sophämtning till Home Assistant

# Features
* Visar nästa sophämtning som state
* Visar vilken typ av sophämtning
* Visar hur många dagar kvar till nästa hämtning

# Manuell installation
Placera custom_components/ha_pireva katalogen i custom_components-katalogen i din Home Assistant och starta om Home Assistant.

# Configuration
Integrationen frågar efter adress och husnummer. Fyll i en giltig adress så skapas sensorn.
Om adressen inte är giltig så accepteras den i alla fall och det skrivs ett felmeddelande i loggarna.

För kontroll av adressen testa den mot https://www.pireva.se/tomningsschema/address-nummer/?output=json
t.ex. https://www.pireva.se/tomningsschema/sundsgatan-41/?output=json

