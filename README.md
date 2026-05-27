# Gesture Media Control

Controlează muzica, videoclipurile, modul ecran complet și volumul folosind
gesturi ale mâinii surprinse de camera web.

Proiect realizat cu **Python**, **MediaPipe**, **OpenCV**, **PyAutoGUI** și
**PyCAW** pentru controlul audio integrat în Windows.

## Ce Face Aplicația

Gesture Media Control urmărește o mână în timp real, recunoaște gesturi
intenționate și le transformă în comenzi multimedia. Fereastra camerei afișează
gestul detectat, ultima acțiune executată, starea degetelor, durata de
menținere a gestului și informații despre controlul dinamic al volumului.

| Gest | Acțiune |
| --- | --- |
| Palmă deschisă | Redare / pauză |
| Degetul mare spre dreapta | Elementul multimedia următor |
| Degetul mare spre stânga | Elementul multimedia anterior |
| Arătătorul în sus | Crește volumul sistemului |
| Arătătorul în jos | Scade volumul sistemului |
| Două degete ridicate | Dezactivează / activează sunetul |
| Ciupire, apoi arătătorul în sus și degetul mare lateral | Ecran complet |
| Patru degete întinse, înclinate în sus sau în jos | Volumul aplicației active |

Gestul dinamic pentru volum ajustează sesiunea audio Windows a aplicației
aflate în prim-plan, atunci când aceasta este disponibilă. O înclinare mai
accentuată aplică mai mulți pași de volum simultan.

## Funcționalități Principale

- Urmărirea în timp real a reperelor mâinii prin camera web
- Timpi de menținere și pauze între comenzi pentru a reduce activările accidentale
- Comandă de ecran complet adaptată pentru YouTube și VLC
- Reglarea volumului aplicației active, atunci când aceasta expune o sesiune audio Windows
- Afișaj live pentru verificarea gesturilor și a pragurilor de detectare

## Cerințe

- Windows
- Python `3.10`, `3.11` sau `3.12`
- O cameră web

Proiectul folosește API-ul clasic `mp.solutions.hands`. Dependența fixată
`mediapipe==0.10.14` este recomandată deoarece unele combinații mai noi de
Python și MediaPipe pot să nu expună acest API.

## Pornire Rapidă

1. Clonează repository-ul și deschide folderul proiectului.

2. Creează și activează un mediu virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instalează dependențele:

   ```powershell
   pip install -r requirements.txt
   ```

4. Reține că aplicația trimite implicit comenzi multimedia reale către
   sistem. Pentru un test doar vizual, setează `USE_PYAUTOGUI = False` în
   [gesture_constants.py](gesture_constants.py) înainte de pornire.

5. Pornește aplicația:

   ```powershell
   python .\gesture_media_control.py
   ```

6. Menține un gest recunoscut în fața camerei. Apasă `q` pentru a închide
   fereastra camerei.

## Comenzi Și Comportament

Executarea comenzilor este activată implicit prin `USE_PYAUTOGUI = True` în
[gesture_constants.py](gesture_constants.py). Pentru a testa detectarea
gesturilor fără a trimite comenzi multimedia reale, setează valoarea la
`False`:

```python
USE_PYAUTOGUI = False
```

### Ecran Complet

Gestul pentru ecran complet alege scurtătura în funcție de aplicația aflată în
prim-plan:

| Aplicație activă | Tastă trimisă |
| --- | --- |
| YouTube în Chrome, Edge, Firefox, Brave sau Opera | `F` |
| VLC | `F` |
| Alte aplicații | `F11` |

Scurtătura implicită de rezervă poate fi schimbată în
[gesture_constants.py](gesture_constants.py):

```python
DEFAULT_FULLSCREEN_BINDING = "f11"
```

### Volumul Dinamic Al Aplicației

Cu patru degete întinse și degetul mare pliat, înclină degetele pentru a regla
volumul sesiunii audio a aplicației aflate în prim-plan. Dacă nu este detectată
o sesiune audio Windows compatibilă, aplicația încearcă tastele configurate ca
variantă de rezervă. Efectul acestor taste depinde de aplicația aflată în
prim-plan.

```python
APP_VOLUME_STEP = 0.05
DEFAULT_APP_VOLUME_UP_BINDING = "up"
DEFAULT_APP_VOLUME_DOWN_BINDING = "down"
```

## Configurare

Valorile pentru reglaj fin se află în
[gesture_constants.py](gesture_constants.py).

| Setare | Rol | Valoare implicită |
| --- | --- | --- |
| `COMMAND_HOLD_TIME` | Timpul necesar înainte de activarea unei comenzi standard | `0.35` s |
| `COMMAND_COOLDOWN` | Pauza dintre comenzile standard | `1.2` s |
| `VOLUME_HOLD_TIME` | Timpul necesar înainte de activarea unei comenzi de volum | `0.2` s |
| `VOLUME_COOLDOWN` | Pauza dintre comenzile repetate de volum | `0.25` s |
| `VOLUME_REPEAT_DELAY` | Întârzierea înainte de repetarea continuă a volumului | `1.0` s |
| `APP_VOLUME_STEP` | Variația volumului la fiecare pas dinamic | `0.05` |
| `PINCH_ARM_TIMEOUT` | Timpul disponibil pentru completarea gestului de ecran complet | `2.0` s |

## Structura Proiectului

| Fișier | Responsabilitate |
| --- | --- |
| [gesture_media_control.py](gesture_media_control.py) | Punctul de pornire al aplicației |
| [gesture_app.py](gesture_app.py) | Bucla camerei web, ciclul gesturilor și informațiile afișate |
| [gesture_detection.py](gesture_detection.py) | Recunoașterea gesturilor statice și dinamice |
| [gesture_helpers.py](gesture_helpers.py) | Calcule geometrice și determinarea stării degetelor |
| [gesture_actions.py](gesture_actions.py) | Trimiterea tastelor, contextul aplicației active și sesiunile audio |
| [gesture_constants.py](gesture_constants.py) | Scurtături, praguri, timpi și opțiuni |

## Limitări Cunoscute

- Este urmărită o singură mână la un moment dat.
- Calitatea detectării depinde de iluminare, claritatea camerei și poziția mâinii.
- Controlul volumului aplicației active folosește funcționalități specifice Windows.
- Tastele de rezervă pentru volumul aplicației nu au același efect în toate programele.

## Rezolvarea Problemelor

| Problemă | Soluție recomandată |
| --- | --- |
| Fereastra camerei nu se deschide | Verifică dacă o altă aplicație folosește camera web. |
| Lipsește `mp.solutions` | Folosește Python `3.10`-`3.12` și reinstalează dependențele din `requirements.txt`. |
| Gesturile se activează prea ușor sau prea greu | Ajustează timpii și pragurile din [gesture_constants.py](gesture_constants.py). |
| Volumul aplicației active folosește tastele de rezervă | Asigură-te că aplicația activă redă sunet și expune o sesiune audio Windows; comportamentul tastelor depinde de program. |

## Confidențialitate

Cadrele video sunt procesate local doar cât timp aplicația rulează. Proiectul
nu implementează înregistrarea camerei sau transmiterea imaginilor prin rețea.
