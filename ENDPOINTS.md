# My Festival API — endpoint-dokumentti / endpoint document

> FI: Täytä tämä pohja ja palauta se Moodleen (Markdown tai PDF, 1–2 sivua). Korvaa kaikki `<…>`-kohdat.
> Esimerkkivastaukset kopioit oman julkisen rajapintasi oikeista vastauksista (selain tai `curl.exe`/`curl`).


**Tekijä / Author:** Olli Luhtanen
**Julkinen osoite / Public URL:** `https://festival-api-festival-luhtanen.2.rahtiapp.fi/`
**GitHub:** `https://github.com/Olli-Luhtanen/my-festival-api`
**Tarkistimen tulos / Checker result:** `20/20 checks passed` (liitä koko tuloste palautukseen / attach the full output)

---

## 1. Endpointit / Endpoints

| Metodi / Method | Polku / Path | Onnistuu / Success | Virheet / Errors |
|---|---|---|---|
| GET | `/api/artists` | 200 | – |
| GET | `/api/days` | 200 | – |
| GET | `/api/stages` | 200 | – |
| GET | `/api/artists/{id}/events` | 200 | 404 |
| GET | `/api/timetable?day=YYYY-MM-DD` | 200 | 400 |
| POST | `/api/events` | 201 | 400 |
| DELETE | `/api/events/{id}` | 204 | 404 |

## 2. Esimerkit / Examples

Kirjoita jokaisesta endpointista esimerkkikutsu ja (lyhennetty) vastaus. Malli:
For every endpoint, write an example call and a (shortened) response. Example:

### GET /api/artists

```bash
curl.exe https://festival-api-festival-luhtanen.2.rahtiapp.fi/api/artists
```
```json
[{"artist_id": 6, "country": "UK", "name": "Adele"}, …]
```

### GET /api/artists/{id}/events
```bash
curl.exe https://festival-api-festival-luhtanen.2.rahtiapp.fi/api/artists/1/events
```
```json
[{"date":"2026-07-10","event_id":1,"stage":"Main A","start_dt":"2026-07-10 18:00:00"}]
```
Tuntematon id / unknown id → `404 koodi ja {"error":"Artist not found"}`

### GET /api/timetable?day=YYYY-MM-DD
```bash
curl.exe https://festival-api-festival-luhtanen.2.rahtiapp.fi/api/timetable?day=2026-07-10
```
```json
[{"artist":"Beyonc\u00e9","date":"2026-07-10","ends":"19:00:00","stage":"Main A","starts":"18:00:00"},...]
```
Virheellinen päivämäärä / invalid date → `400 ja {"error":"day must be YYYY-MM-DD"}`

### POST /api/events
Komennon ajamisen kanssa oli pieni ongelma, mutta tämä meni läpi oikein, kun vaan tallensi json tiedostoon datan tässä käytin seuraavaa
{"artist_id": 1, "stage_id": 3, "day_id": 2, "start_dt": "2026-07-11 21:00:00"}
```bash
curl.exe -X POST https://festival-api-festival-luhtanen.2.rahtiapp.fi/api/events -H "Content-Type: application/json" -d "@body.json  
```
```json
201 CREATED
date...
content type...
...
{"artist_id":1,"day_id":2,"duration_min":45,"end_dt":"2026-07-11 21:45:00","event_id":16,"stage_id":3,"start_dt":"2026-07-11 21:00:00"}
```
Puuttuva kenttä → `400 BAD REQUEST... {"error":"Missing field(s): start_dt"}` · 
Olematon artist_id / unknown artist_id → `400 BAD REQUEST... {"error":"Invalid artist_id, stage_id or day_id: referenced row does not exist"}`

### DELETE /api/events/{id}
Post kohdassa luotu event poistetaan tässä.
```bash
curl.exe -i -X DELETE https://festival-api-festival-luhtanen.2.rahtiapp.fi/api/events/16
```
Onnistuu / success → `204 NO CONTENT` · Tuntematon id / unknown id → `404 NOT FOUND... {"error":"Event not found"}`

## 3. Julkaisu Rahtiin / Deploying to Rahti (3–6 lausetta / sentences)

Julkaisin valmiin koodin githubiin julkiseksi repoksi jonka osoitteen annoin Rahdille.
Se luki sen läpi ja löysi docker tiedostot jonka perusteella se rakensi kontin sovellukselle. Varmistin asetukset ja rajat cpu ja muistin käytölle.
Pienen hetken jälkeen kontti ja sovellus oli käynnissä.
Osoite oli yhdistelmä kontille annetusta nimestä, projekti nimestä ja loppuun tietenkin reitit api/jne...

Project details workload tabista löytyi itse festival-api ja sieltä linkki "sivulle"

Ongelmiin en törmännyt csc puolella muuta kuin kesti hetken löytää mistä lisään/importtaan gitin kautta add napista puhuttiin ja löysin +napin hetken kuluttua kun olin ensin etsinyt sitä projektin puolelta.
Muuten kaikki toimi odotetusti.


## 4. Tietoturva / Security (2–4 lausetta / sentences)
SQL injektio on hyvin suojattu jo nyt kun kaikki kyselyt on parametrisoituja ? avulla. Lisäksi syötettä validoidaan ettei esim id kenttänä voi olla kirjainta tai datetime jäsennetään ettei ylimääräistä pääse läpi.

Tuotantoon kuitenkaan tämä ei ole valmis koska se on täysin avoin. Kuka tahansa joka tietää tai löytää osoitteen voi saada kasiksi tai muokata kantaa.
Vaadittaisiin tunnistautumista, valtuudet vain tietyillä ihmisillä/avaimilla, rate limittejä, Lisää virheenkäsittelyä ja valvontaa.
Myös itse tietokanta saattaisi muuttua isompaan tietokantapalveluun sqliten sijasta joka ei tässä toteutuksessa ole pysyvä vaan resetoi uuden buildin yhteydessä.