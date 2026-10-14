# My Festival API — M10 (CSC Rahti)

---

## Suomeksi

Tämä kansio on M10-tehtävän lähtöpohja. Lisää siihen oma `myfestival.db`, toteuta TODO-kohdat
tiedostossa `app.py` ja julkaise sovellus CSC:n Rahti-konttipilveen.

| Tiedosto | Mitä se tekee |
|---|---|
| `app.py` | Flask-sovellus. `GET /api/artists`, `/api/days` ja `/api/stages` ovat valmiit; muut reitit ovat TODO. |
| `myfestival.db` | Festivaalikanta. Korvaa omalla My Festival -kannallasi. |
| `requirements.txt` | Python-riippuvuudet (Flask, gunicorn). |
| `Dockerfile` | Ohje, jolla Rahti rakentaa kontin. Ei tarvitse muokata. |
| `test_endpoints.py` | Tarkistin (20 tarkistusta). Hakee tunnisteet sinun kannastasi, lisää testirivin ja poistaa sen. Kaiken pitää olla vihreää. |
| `ENDPOINTS.md` | Endpoint-dokumentin pohja. Täytä ja palauta Moodleen. |
| `deploy_rahti.sh` | Valinnainen: julkaisu komentoriviltä web-konsolin sijaan. |

### 1. Aja paikallisesti
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                      # → http://localhost:8080/api/artists
python test_endpoints.py http://localhost:8080   # toisessa terminaalissa
```
Windows PowerShell: `curl` on eri ohjelma — käytä `curl.exe`:ä, selainta tai tarkistinta.
Jos `python`-komentoa ei löydy, kokeile `python3` (Windowsissa myös `py`).
`localhost` on vain oman koneesi osoite. Lähtöpohjan TODO-reitit palauttavat 501, joten 20/20 on tavoite vasta toteutuksen jälkeen.

### 2. Vie GitHubiin
Luo GitHubiin **julkinen** repo (esim. `my-festival-api`). Voit tehdä ensimmäisen viennin selaimessa:
valitse uuden repon luomisessa README, avaa repo, paina **Add file → Upload files**, valitse tämän
kansion tiedostot ja paina **Commit changes**. Erillistä `git push` -komentoa ei silloin tarvita.
Vaihtoehtoisesti tee commit omalla koneellasi ja pushaa se Gitiä tai GitHub Desktopia käyttäen.
Tiedostojen pitää olla repon juuressa (Dockerfile ylimmällä tasolla), ei `starter/`-alikansiossa.
Tarkista ennen latausta, ettei mukana ole `.venv`-kansiota, salasanoja, tokeneita tai henkilötietoja.

### 3. Julkaise Rahtiin (web-konsoli)
1. Kirjaudu <https://console.rahti.csc.fi> (CSC-tunnus tai Haka).
2. **Create Project** → *Name:* `festival-<csc-tunnuksesi>` → *Description:* `csc_project: 2021201`
   (kurssin CSC-projektin numero, tarkista Moodlesta).
3. Avaa projektissa **Add** → **Import from Git** → liitä repon URL.
   Rahti tunnistaa Dockerfilen; jos saat ilmoituksen *Multiple import strategies detected*,
   käytä suositeltua strategiaa **Dockerfile**.
4. *Name:* `festival-api`. Varmista, että **Create a route** on valittuna.
   Avaa *Show advanced Routing options* → valitse **Secure Route**, *TLS termination: Edge*,
   *Insecure traffic: Redirect*.
5. *Target port:* **8080**. Avaa **Resource limits** ja aseta:
   CPU request **50** millicores, CPU limit **250** millicores,
   Memory request **128 Mi**, Memory limit **256 Mi** (kurssin kiintiö on yhteinen!).
6. **Create**. Rakentuminen kestää muutaman minuutin. *Topology*-näkymässä nuolikuvake avaa julkisen
   osoitteen, joka päättyy `rahtiapp.fi` (usein muodossa `...2.rahtiapp.fi`). Kopioi se sieltä.
7. Aja tarkistin julkista osoitetta vasten:
   `python test_endpoints.py https://<osoitteesi>`

**Muutokset koodiin:** pushaa GitHubiin ja paina Rahdissa *Builds → festival-api → Start build*
(tai lisää GitHub-webhook, jolloin build käynnistyy automaattisesti).

### Hyvä tietää
- Rahti ajaa kontin satunnaisella käyttäjä-id:llä. Dockerfile antaa sille kirjoitusoikeuden kantaan.
- SQLite kulkee imagessa: POST-lisäykset **katoavat**, kun uusi Pod tai build ottaa käyttöön
  imagen mukana pakatun kannan. Säilytä alkuperäinen kanta myös omalla koneellasi.
  Tämä on tehtävässä hyväksyttyä.
- Kaikki saman CSC-projektin jäsenet näkevät toistensa Rahti-projektit. Älä muuta muiden projekteja.
- Kurssin jälkeen poista projektisi: *Project → Actions → Delete project*.
