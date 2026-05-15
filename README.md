# Mobile Devices Info

Integrazione custom per Home Assistant che raccoglie e centralizza le informazioni sui dispositivi mobili registrati tramite l'app **Home Assistant Companion** (`mobile_app`).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1.0%2B-blue)

---

## ✨ Caratteristiche

- **Sensore unificato**: espone in un unico attributo la lista di tutti i dispositivi mobili trovati in HA
- **Selezione dispositivi notificabili**: configura quali dispositivi ricevono notifiche push
- **Numero di telefono per dispositivo**: associa un numero di telefono a ciascun device (utile per automazioni SMS tramite integrazioni come [fritz_automation](https://github.com/acolmano/fritz_automation))
- **Aggiornamento in tempo reale**: il sensore si aggiorna automaticamente al salvataggio delle opzioni
- **Compatibile HACS**: installabile e aggiornabile direttamente da Home Assistant Community Store

---

## 📦 Installazione tramite HACS

1. Apri HACS in Home Assistant
2. Vai su **Menu (⋮) → Custom repositories**
3. Inserisci `https://github.com/acolmano/mobile_devices_info` e seleziona la categoria **Integration**
4. Clicca **Add**, poi cerca *Mobile Devices Info* e installala
5. Riavvia Home Assistant
6. Vai in **Impostazioni → Dispositivi e Servizi → Aggiungi Integrazione** e cerca *Mobile Devices Info*

### Installazione manuale

1. Copia la cartella `custom_components/mobile_devices_info/` in `/config/custom_components/`
2. Riavvia Home Assistant
3. Aggiungi l'integrazione da **Impostazioni → Dispositivi e Servizi**

---

## ⚙️ Configurazione

### Primo avvio

Al momento dell'aggiunta dell'integrazione viene mostrato un form con la selezione dei dispositivi da notificare. È possibile saltare questo step e configurare tutto in seguito dalle opzioni.

### Opzioni (modificabili in qualsiasi momento)

Dalla pagina dell'integrazione clicca **Configura**:

| Campo | Descrizione |
|---|---|
| **Dispositivi da notificare** | Selezione multipla dei device che devono ricevere notifiche push |
| **phone_NomeDevice** | Numero di telefono associato al dispositivo (es. `+393331234567`) |

I numeri di telefono vengono salvati in `options["phone_numbers"]` come dizionario `{device_id: numero}`.

---

## 📊 Sensore

### `sensor.mobile_devices_info`

| Proprietà | Valore |
|---|---|
| **State** | Numero di dispositivi con `notificare: true` |
| **Icona** | `mdi:cellphone-information` |

#### Attributi (`extra_state_attributes.devices`)

Lista di dizionari, uno per ogni dispositivo `mobile_app` trovato:

```yaml
devices:
  - name: "iPhone di Mario"
    identity: "iphone_di_mario"
    notify_id: "notify.mobile_app_iphone_di_mario"
    notificare: true
    phone_number: "+393331234567"
  - name: "Pixel di Lucia"
    identity: "pixel_di_lucia"
    notify_id: "notify.mobile_app_pixel_di_lucia"
    notificare: false
    phone_number: null
```

---

## 🤖 Esempi di Automazione

### Notifica push a tutti i dispositivi notificabili

```yaml
automation:
  - alias: "Notifica a tutti i dispositivi"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_sensor
        to: "on"
    action:
      - repeat:
          for_each: "{{ state_attr('sensor.mobile_devices_info', 'devices') | selectattr('notificare', 'eq', true) | list }}"
          sequence:
            - service: "{{ repeat.item.notify_id }}"
              data:
                message: "Movimento rilevato!"
```

### Invio SMS tramite fritz_automation

```yaml
automation:
  - alias: "SMS su allarme"
    trigger:
      - platform: state
        entity_id: alarm_control_panel.home
        to: "triggered"
    action:
      - repeat:
          for_each: "{{ state_attr('sensor.mobile_devices_info', 'devices') | selectattr('phone_number') | list }}"
          sequence:
            - service: fritz_automation.send_sms
              data:
                target: "{{ repeat.item.phone_number }}"
                message: "Allarme attivato in casa!"
```

---

## ⚠️ Compatibilità

- **Home Assistant**: versione 2024.1.0 o successiva
- **Dipendenze**: nessuna dipendenza esterna Python
- **Integrazioni richieste**: almeno un dispositivo con l'app [Home Assistant Companion](https://companion.home-assistant.io/) installata e registrata

---

## 🔄 Aggiornamenti

Tramite HACS, gli aggiornamenti vengono notificati automaticamente. Dopo ogni aggiornamento riavvia Home Assistant.

---

## 📚 Documentazione

- [CHANGELOG.md](CHANGELOG.md) — cronologia delle versioni
- [Issues](https://github.com/acolmano/mobile_devices_info/issues) — segnalazione bug e richieste di funzionalità
