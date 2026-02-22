# MyERPCompanion

MyERPCompanion to system ERP wspierający procesy sprzedażowe, zakupowe, magazynowe, administracyjne i raportowe.  
Aplikacja obejmuje warstwę API (`FastAPI`), moduł AI do prognoz sprzedaży (`PyTorch`) oraz interfejsy klienckie (`desktop-app`, `web-app`, `mobile-app`).  
Poniżej znajduje się instrukcja uruchomienia środowiska.

## Instrukcja Uruchomienia

Wszystkie komendy `docker compose` należy uruchamiać z katalogu, w którym znajduje się plik `docker-compose.yml`.
Zalecane jest wykonywanie całej sekwencji uruchomieniowej w środowisku `WSL2` (`Ubuntu`), aby ograniczyć problemy zgodności.

## 1. Wymagania
- `Docker` (z pluginem `docker compose`)
- `WSL2` z `Ubuntu 24.04 LTS` (wymagane tylko dla natywnego `desktop-app`)
- dla `desktop-app-web` wystarczy `docker compose` uruchamiany z `PowerShell`
- wolne porty: `5432`, `8000`, `8550`, `8551`, `8552`

## 2. Sekwencja uruchomienia

### Krok 1. Build wszystkich kontenerów
```bash
docker compose build
```

Uwaga: ten krok może potrwać nawet kilkanaście minut, głównie przez rozmiar bibliotek używanych w `ai-app` (m.in. PyTorch).

### Krok 2. Start bazy danych PostgreSQL
```bash
docker compose up -d postgres
```

### Krok 3. Zbudowanie migracji Alembic
```bash
docker compose run --rm rest-api alembic revision --autogenerate
```

Uwaga: polecenie `alembic revision --autogenerate` tworzy nowy plik migracji przy każdym uruchomieniu.  
W standardowym przebiegu krok należy wykonać jednokrotnie.

### Krok 4. Wysłanie migracji do bazy
```bash
docker compose run --rm rest-api alembic upgrade head
```

Uwaga: w standardowym przebiegu krok należy wykonać jednokrotnie.

### Krok 5. Start `rest-api`
```bash
docker compose up rest-api
```

### Krok 6. Start `ai-app`  (osobny terminal)
W drugim terminalu należy uruchomić:

```bash
docker compose up ai-app
```

Uwaga: pierwszy run `ai-app` może potrwać kilkanaście minut (trenowanie modelu i zapis wyników).

### Krok 7. Start `desktop-app` (osobny terminal)
W kolejnym, osobnym terminalu należy uruchomić:

```bash
LOCAL_UID=$(id -u) LOCAL_GID=$(id -g) \
WAYLAND_HOST_RUNTIME_DIR=/mnt/wslg/runtime-dir \
WAYLAND_DISPLAY=wayland-0 \
docker compose up desktop-app
```

Dla wersji natywnej przykładowe zdjęcia do dodania są dostępne wewnątrz kontenera w katalogu `sample_images`.

W przypadku problemów z uruchomieniem wersji natywnej, w dalszej części instrukcji znajduje się wersja alternatywna `desktop-app-web`.

### Krok 8. Start `web-app` (osobny terminal)
W kolejnym, osobnym terminalu należy uruchomić:

```bash
docker compose up web-app
```

Następnie należy otworzyć:
`http://localhost:8551`

Po otwarciu widoku zalecane jest wykonanie twardego odświeżenia przeglądarki (`Ctrl+F5`).

### Krok 9. Start `mobile-app` (osobny terminal)
W kolejnym, osobnym terminalu należy uruchomić:

```bash
docker compose up mobile-app
```

Następnie należy otworzyć:
`http://localhost:8552`

Po otwarciu widoku zalecane jest wykonanie twardego odświeżenia przeglądarki (`Ctrl+F5`).

## 3. Adresy aplikacji
- API: `http://localhost:8000`
- Desktop natywny: okno aplikacji Flet (bez adresu URL)
- Desktop (wersja web): `http://localhost:8550`
- Web app: `http://localhost:8551`
- Mobile app (web preview): `http://localhost:8552`

Uwaga dla widoków webowych (`desktop-app-web`, `web-app`, `mobile-app`): po otwarciu adresu należy wykonać twarde odświeżenie (`Ctrl+F5`).

## 4. Połączenie z PostgreSQL (bezpośrednie)
Po uruchomieniu kontenera `postgres` dostępne jest bezpośrednie połączenie do bazy:
- host: `localhost`
- port: `5432`
- baza danych: `MyERPCompanion`
- użytkownik: `postgres`
- hasło: `changeme`

Przykładowy URI:
`postgresql://postgres:changeme@localhost:5432/MyERPCompanion`

## 5. Logowanie
- konto administracyjne: `admin` / `haslo123`
- przykładowi pracownicy: np. `madminowski` / `haslo123`
- konta klientów (portal web): `customer001` ... `customer040`, hasło: `haslo123`

## 6. Wersja web `desktop-app` (gdy wersja natywna nie startuje)
Jeśli wersja natywna nie startuje, nie wyświetla okna lub ma problemy z Wayland/X11:

1. Należy zatrzymać natywny desktop:
```bash
docker compose stop desktop-app
```
2. Następnie należy uruchomić wersję web desktopu:
```bash
docker compose up desktop-app-web
```
3. Należy otworzyć:
`http://localhost:8550`

Po otwarciu widoku zalecane jest wykonanie twardego odświeżenia przeglądarki (`Ctrl+F5`).

To jest funkcjonalny odpowiednik desktopu, niewymagający lokalnego GUI w kontenerze.
Wersję `desktop-app-web` można uruchamiać również z `PowerShell` (z użyciem `docker compose`).

Dla wersji web przykładowe zdjęcia do dodania są dostępne w katalogu głównym projektu: `sample_images`.

## 7. Zatrzymanie środowiska
```bash
docker compose down
```

Pełne czyszczenie danych (łącznie z wolumenami bazy):
```bash
docker compose down -v
```

## 8. Diagnostyka (podstawowe komendy)
Sprawdzenie statusu kontenerów:

```bash
docker compose ps
```

Podgląd logów `rest-api`:

```bash
docker compose logs -f rest-api
```

Podgląd logów `ai-app`:

```bash
docker compose logs -f ai-app
```

## 9. Problemy z populacją bazy
W przypadku problemów z inicjalizacją/populacją bazy należy usunąć wolumeny i ponownie wykonać migracje.

Najpierw należy zatrzymać środowisko i usunąć wolumeny projektu:

```bash
docker compose down -v
```

Jeśli wymagane jest ręczne usunięcie wolumenów projektu, można użyć:

```bash
docker volume rm myerpcompanion_postgres-data myerpcompanion_media-data myerpcompanion_desktop-app-web-upload-data
```

Uwaga: powyższa komenda usuwa tylko wolumeny projektu MyERPCompanion.

Następnie należy ponownie wykonać kroki:
- krok 2 (start `postgres`)
- krok 3 (zbudowanie migracji Alembic) tylko po usunięciu istniejącego pliku rewizji migracji z katalogu:
  `rest-api/rest_api/migrations/versions/`
- krok 4 (wysłanie migracji do bazy)

Jeżeli plik migracji już istnieje, krok 3 należy pominąć i przejść bezpośrednio do kroku 4.
