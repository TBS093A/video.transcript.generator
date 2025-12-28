# Video Transcript Generator

Skrypt do automatycznego generowania transkrypcji z plików wideo/audio przy użyciu OpenAI Whisper.  
Opcjonalnie pobiera treści z YouTube przy użyciu yt-dlp.

## Wymagania systemowe

FFmpeg jest **wymagany** - Whisper używa go do dekodowania plików audio/video. Skrypt nie uruchomi się bez FFmpeg.

### macOS (szybka instalacja - statyczny binary)

```bash
# Pobierz statyczny ffmpeg (~50MB, bez kompilacji)
curl -L https://evermeet.cx/ffmpeg/ffmpeg-7.1.1.zip -o ffmpeg.zip
curl -L https://evermeet.cx/ffmpeg/ffprobe-7.1.1.zip -o ffprobe.zip

# Rozpakuj i zainstaluj
unzip ffmpeg.zip && unzip ffprobe.zip
sudo mv ffmpeg ffprobe /usr/local/bin/
rm ffmpeg.zip ffprobe.zip

# Sprawdź
ffmpeg -version
```

### macOS (Homebrew - wolniejsza, pełna instalacja)

```bash
brew install ffmpeg
```

### Linux (szybka instalacja - statyczny binary)

```bash
# Pobierz statyczny ffmpeg (~80MB, bez zależności)
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz

# Rozpakuj i zainstaluj
tar xf ffmpeg.tar.xz
sudo mv ffmpeg-*-static/ffmpeg ffmpeg-*-static/ffprobe /usr/local/bin/
rm -rf ffmpeg.tar.xz ffmpeg-*-static

# Sprawdź
ffmpeg -version
```

### Ubuntu/Debian (apt)

```bash
sudo apt install ffmpeg
```

### Windows (szybka instalacja - statyczny binary)

```powershell
# Pobierz z gyan.dev (najpopularniejsze buildy dla Windows)
# 1. Wejdź na: https://www.gyan.dev/ffmpeg/builds/
# 2. Pobierz "ffmpeg-release-essentials.zip" (~80MB)
# 3. Rozpakuj i dodaj folder bin/ do PATH

# Lub przez PowerShell:
Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile ffmpeg.zip
Expand-Archive ffmpeg.zip -DestinationPath C:\ffmpeg
# Dodaj C:\ffmpeg\ffmpeg-*-essentials_build\bin do zmiennej PATH

# Sprawdź
ffmpeg -version
```

### Windows (package manager)

```bash
choco install ffmpeg
# lub: winget install ffmpeg
```

## Instalacja

```bash
# Utwórz wirtualne środowisko Python
python3 -m venv venv

# Aktywuj środowisko
source venv/bin/activate  # Linux/macOS
# lub: venv\Scripts\activate  # Windows

# Zainstaluj zależności
pip install -r requirements.txt
```

## Struktura projektu

```
video.transcript.generator/
├── transcribe.py       # Główny skrypt
├── requirements.txt    # Zależności Python
├── venv/               # Wirtualne środowisko Python (ignorowane przez git)
└── videos/             # Workspace - miejsce na media i transkrypcje (ignorowane przez git)
    ├── bulk.urls.txt   # Opcjonalny plik z linkami YouTube/playlistami
    ├── .downloaded_archive.txt  # Archiwum pobranych (automatyczne)
    ├── Nazwa Playlisty/         # Subfolder dla playlisty
    │   ├── 001 - Pierwszy film.webm
    │   ├── 001 - Pierwszy film.transcript.txt
    │   ├── 002 - Drugi film.webm
    │   └── 002 - Drugi film.transcript.txt
    ├── Pojedynczy film.webm
    ├── Pojedynczy film.transcript.txt
    └── ...
```

> 💡 **Tip:** Folder `videos/` to domyślny workspace skryptu - umieść tam pliki wideo/audio lub `bulk.urls.txt` z linkami YouTube. Skrypt przeszukuje folder rekursywnie, więc możesz organizować pliki w podfolderach. Folder `venv/` zawiera wirtualne środowisko Python. Oba foldery są ignorowane przez git.

## Użycie

### Podstawowe użycie

```bash
# Transkrypcja plików wideo/audio z folderu videos/ (model medium, język polski)
python transcribe.py

# Z wyborem modelu i języka
python transcribe.py --model large --language en

# Tryb audio-only (pobiera audio z YouTube, przetwarza tylko pliki audio)
python transcribe.py --audio-only

# Pomiń pobieranie z YouTube
python transcribe.py --skip-download
```

Skrypt automatycznie:
- Używa folderu `videos/` jako workspace (tworzy go jeśli nie istnieje)
- Przeszukuje folder **rekursywnie** (włącznie z podfolderami)
- Zapisuje transkrypcje **obok plików media** (w tej samej lokalizacji)
- Tworzy **subfoldery dla playlist** z numerowanymi plikami
- **Pomija już pobrane** filmy (archiwum pobierania)

### Tryb audio-only

Użyj flagi `--audio-only` aby:
- Pobierać tylko audio z YouTube w oryginalnym formacie (webm/m4a - bez konwersji)
- Przetwarzać tylko pliki audio (ignoruje pliki wideo)
- Mniejsze pliki, szybsze pobieranie

```bash
python transcribe.py --audio-only
```

### Pobieranie z YouTube (bulk)

Utwórz plik `videos/bulk.urls.txt` z linkami do filmów lub playlist (jeden na linię):

```
https://youtu.be/XXXXX
https://www.youtube.com/watch?v=YYYYY
# komentarze są ignorowane
https://www.youtube.com/playlist?list=PLxxxxxxxx
```

Następnie uruchom skrypt:

```bash
python transcribe.py
```

**Obsługa playlist:**
- Playlisty są pobierane do subfolderów (nazwa playlisty)
- Pliki są numerowane według kolejności: `001 - Tytuł.webm`, `002 - Tytuł.webm`, ...
- Już pobrane filmy są pomijane (archiwum w `.downloaded_archive.txt`)

Skrypt automatycznie:
1. Pobierze treści z YouTube (wideo lub audio w zależności od trybu)
2. Pominie pobieranie plików, które mają już transkrypcję
3. Wygeneruje transkrypcje dla wszystkich plików bez transkrypcji

### Opcje

| Opcja | Domyślnie | Opis |
|-------|-----------|------|
| `--model` | `medium` | Model Whisper: tiny, base, small, medium, large |
| `--language` | `pl` | Język audio |
| `--audio-only` | - | Używaj tylko plików audio |
| `--skip-download` | - | Pomiń pobieranie z YouTube |

## Dostępne modele Whisper

| Model  | Rozmiar | VRAM  | Jakość        |
|--------|---------|-------|---------------|
| tiny   | 39M     | ~1GB  | Najszybszy    |
| base   | 74M     | ~1GB  | Szybki        |
| small  | 244M    | ~2GB  | Dobry         |
| medium | 769M    | ~5GB  | Bardzo dobry  |
| large  | 1550M   | ~10GB | Najlepszy     |

## Obsługiwane formaty

**Wideo:** `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.flv`, `.wmv`, `.m4v`, `.mpeg`, `.mpg`

**Audio:** `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.opus`, `.aac`, `.wma`

## Pliki wyjściowe

Transkrypcje są zapisywane **obok plików media** z rozszerzeniem `.transcript.txt`:

```
videos/video.mp4 → videos/video.transcript.txt
videos/podcast.mp3 → videos/podcast.transcript.txt
videos/kurs/lekcja1.mkv → videos/kurs/lekcja1.transcript.txt
```

## Logika pomijania

Skrypt inteligentnie pomija:
- ⏭️ Pobieranie treści z YouTube, które mają już transkrypcję
- ⏭️ Transkrypcję plików, które mają już plik `.transcript.txt`

Dzięki temu można wielokrotnie uruchamiać skrypt bez ponownego przetwarzania.

## Akceleracja GPU

Skrypt automatycznie wykrywa i używa najlepszego dostępnego urządzenia:

| Urządzenie | Wykrywanie | Opis |
|------------|------------|------|
| **NVIDIA GPU** | `torch.cuda.is_available()` | Najszybsze dla kart NVIDIA (wymaga CUDA) |
| **Apple Silicon** | `torch.backends.mps.is_available()` | GPU M1/M2/M3 (Metal Performance Shaders) |
| **CPU** | fallback | Wolniejsze, ale zawsze działa |

Przykładowy output:
```
🖥️  Urządzenie: Apple Silicon GPU (MPS)
🤖 Ładuję model Whisper: medium
```

## Wykrywanie FFmpeg

Skrypt sprawdza czy FFmpeg jest zainstalowany przy starcie:
- ✅ **FFmpeg znaleziony** → skrypt działa normalnie
- ❌ **FFmpeg nie znaleziony** → skrypt wyświetla instrukcje instalacji i kończy działanie

FFmpeg jest wymagany przez Whisper do dekodowania plików audio/video.
