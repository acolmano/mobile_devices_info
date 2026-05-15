# Changelog — Mobile Devices Info

## v1.0.0 (2026-05-15) — Release iniziale

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
