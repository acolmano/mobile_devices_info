# Changelog — Mobile Devices Info

## v1.4.0 (2026-05-19)

### ✨ Novità

- Aggiunta selezione **notifiche SMS** nella maschera di configurazione di tutti i tipi di device (registrati e manuali)
- La casella SMS è abilitabile solo se il numero di telefono ha almeno 10 cifre
- Inserendo un numero troppo corto viene mostrato un avviso direttamente nel form

---

## v1.1.0 (2026-05-15)

### 💥 Breaking change

- Abbandonato il config flow basato su options flow. La configurazione ora avviene tramite **subentries**: ogni dispositivo è una voce indipendente, aggiungibile e modificabile singolarmente.

### ✨ Novità

- Ogni device si aggiunge uno alla volta tramite il pulsante **+ Aggiungi dispositivo**
- Per ogni device è possibile impostare: numero di telefono e flag notifiche push
- I device già configurati vengono esclusi dalla lista di selezione
- Ogni device può essere modificato in qualsiasi momento tramite **Riconfigura**
- Requisito minimo HA aggiornato a 2024.11.0 (supporto subentries)

---

## v1.0.0 (2026-05-15) — Release iniziale

### 🎉 Funzionalità

- Sensore `sensor.mobile_devices_info` che espone la lista di tutti i dispositivi `mobile_app` registrati in Home Assistant
- Selezione multipla dei dispositivi da notificare tramite config flow UI
- Associazione di un numero di telefono per ciascun dispositivo, configurabile direttamente dalle opzioni dell'integrazione
- Aggiornamento automatico del sensore al salvataggio delle opzioni
- Compatibilità HACS: struttura `custom_components/mobile_devices_info/` con `hacs.json`
- Brand icon `notify_events` per la visualizzazione nell'UI di HA


### 🎉 Funzionalità

- Sensore `sensor.mobile_devices_info` che espone la lista di tutti i dispositivi `mobile_app` registrati in Home Assistant
- Selezione multipla dei dispositivi da notificare tramite config flow UI
- Associazione di un numero di telefono per ciascun dispositivo, configurabile direttamente dalle opzioni dell'integrazione
- Aggiornamento automatico del sensore al salvataggio delle opzioni
- Compatibilità HACS: struttura `custom_components/mobile_devices_info/` con `hacs.json`
- Brand icon `notify_events` per la visualizzazione nell'UI di HA

### 📊 Sensore

- **State**: numero di dispositivi con flag `notificare: true`
- **Attributo `devices`**: lista completa con `name`, `identity`, `notify_id`, `notificare`, `phone_number`

### 🛠️ Tecnico

- Nessuna dipendenza esterna Python
- Lettura numeri di telefono dalle options della config entry (rimosse dipendenze da integrazioni esterne)
- Lookup stabile tramite `device.id` invece di `device.name`
- Gestione subentries robusta (dict e list)
