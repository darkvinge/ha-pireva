# ha-pireva
Pireva integration för sophämtning till Home Assistant

# Features
* Visar nästa sophämtning som state
* Visar vilken typ av sophämtning
* Visar hur många dagar kvar till nästa hämtning
* Visar datum och typ för efterföljande hämtning

## Attribut
| Attribut | Beskrivning |
| --- | --- |
| `avfallstyp` | Typ av avfall vid nästa hämtning |
| `dagar_till_tomning` | Antal dagar kvar till nästa hämtning |
| `efterfoljande_datum` | Datum för efterföljande hämtning |
| `efterfoljande_avfallstyp` | Typ av avfall vid efterföljande hämtning |

# Manuell installation
Placera custom_components/ha_pireva katalogen i custom_components-katalogen i din Home Assistant och starta om Home Assistant.

# Configuration
Integrationen frågar efter adress och husnummer. Fyll i en giltig adress så skapas sensorn.
Adressen kontrolleras mot Pireva innan den sparas. Om den inte hittas visas ett felmeddelande, och samma adress kan inte läggas till två gånger.

För kontroll av adressen testa den mot https://www.pireva.se/tomningsschema/address-nummer/?output=json
t.ex. https://www.pireva.se/tomningsschema/sundsgatan-41/?output=json

