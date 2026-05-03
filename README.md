# Wind Turbine IoT API 

En REST API til overvågning af vindmøller med automatisk temperatur-alarm system, bygget som del af Predictive Maintenance løsning for Intelligent IoT Solutions A/S.

## 🚀 Live API
API'et kører live på Azure VM:
- **Base URL:** `http://51.103.212.67:5001`
- **Swagger UI:** `http://51.103.212.67:5001/apidocs`

## ⚡ Funktioner
- Opret og administrer vindmøller
- Modtag sensordata fra IoT enheder
- Automatisk alarm hvis temperatur overstiger 75°C
- Alarmdata gemmes i Azure MySQL database
- Email notifikation til serviceteam ved alarm
- CI/CD pipeline via GitHub Actions

## 🛠️ Teknologier
| Teknologi | Formål |
|---|---|
| Python / Flask | REST API framework |
| Azure MySQL | Cloud database persistering |
| Swagger / Flasgger | API dokumentation |
| Gmail SMTP | Email notifikation |
| GitHub Actions | CI/CD deployment |
| Docker | Containerisering |

## 📦 Installation

### Kør lokalt med Python
```bash
git clone https://github.com/Milad2004-dk/turbine-iot.git
cd turbine-iot
pip install -r requirements.txt
python TurbineApi.py
```

### Kør med Docker
```bash
docker build -t turbine-iot .
docker run -p 5001:5001 turbine-iot
```

## 🔑 Environment Variables
Opret følgende environment variables før du kører API'et:
```bash
DB_HOST=din-database-host
DB_USER=dit-brugernavn
DB_PASSWORD=dit-password
DB_NAME=din-database
GMAIL_USER=din-email
GMAIL_PASSWORD=din-app-password
```

## 📡 API Endpoints

| Method | Endpoint | Beskrivelse |
|---|---|---|
| POST | `/sensor-data` | Modtag sensordata fra IoT enhed |
| GET | `/alarms` | Hent alle registrerede alarmer |
| GET | `/turbines` | Hent alle vindmøller |
| POST | `/turbines` | Opret ny vindmølle |
| PUT | `/turbines/<id>` | Opdater vindmølle |
| DELETE | `/turbines/<id>` | Slet vindmølle |

## 🧪 Test med Postman
Send et POST request til `/sensor-data`:
```json
{
  "turbine_id": 1,
  "temperature": 82.5
}
```
Returnerer `status: ALARM` hvis temperatur > 75°C

## 🔄 CI/CD
Push til `main` branchen trigger automatisk deployment til Azure VM via GitHub Actions.
