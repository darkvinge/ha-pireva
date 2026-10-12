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

## Kalender
Integrationen skapar även en kalender-entitet där varje hämtning är en heldagshändelse med avfallstypen som rubrik.
Kalendern syns under **Kalender** i sidomenyn och kan visas på en dashboard med kortet **Kalender**.

Den kan också användas som utlösare i automationer, t.ex. för en påminnelse kvällen innan hämtning:
```yaml
triggers:
  - trigger: calendar
    event: start
    entity_id: calendar.pireva_avfallsschema_sundsgatan_41
    offset: "-6:00:00"
actions:
  - action: notify.notify
    data:
      message: "Ställ ut kärlet för {{ trigger.calendar_event.summary }} i kväll"
```

# Manuell installation
Placera custom_components/ha_pireva katalogen i custom_components-katalogen i din Home Assistant och starta om Home Assistant.

# Configuration
Integrationen frågar efter adress och husnummer. Fyll i en giltig adress så skapas sensorn.
Adressen kontrolleras mot Pireva innan den sparas. Om den inte hittas visas ett felmeddelande, och samma adress kan inte läggas till två gånger.

För kontroll av adressen testa den mot https://www.pireva.se/tomningsschema/address-nummer/?output=json
t.ex. https://www.pireva.se/tomningsschema/sundsgatan-41/?output=json

