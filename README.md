# Video Transcript Generator

Skrypt do automatycznego generowania transkrypcji z plików wideo/audio przy użyciu OpenAI Whisper.  
Opcjonalnie pobiera treści z YouTube przy użyciu yt-dlp.

## Wymagania systemowe

```bash
# FFmpeg (opcjonalny, ale zalecany)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

> ⚠️ **Bez FFmpeg** skrypt automatycznie przełącza się na tryb audio-only (pobiera i przetwarza tylko pliki audio).

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
    ├── bulk.urls.txt   # Opcjonalny plik z linkami YouTube
    ├── subfolder/      # Podfoldery są obsługiwane (rekursywnie)
    │   ├── audio.mp3
    │   └── audio.transcript.txt
    ├── video1.mp4
    ├── video1.transcript.txt
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
- **Wykrywa brak FFmpeg** i automatycznie przełącza się na tryb audio-only

### Tryb audio-only

Użyj flagi `--audio-only` aby:
- Pobierać tylko audio z YouTube (mniejsze pliki, szybsze pobieranie)
- Przetwarzać tylko pliki audio (ignoruje pliki wideo)

```bash
python transcribe.py --audio-only
```

> 💡 Tryb audio-only jest automatycznie włączany gdy FFmpeg nie jest zainstalowany.

### Pobieranie z YouTube (bulk)

Utwórz plik `videos/bulk.urls.txt` z linkami do filmów (jeden na linię):

```
https://youtu.be/XXXXX
https://www.youtube.com/watch?v=YYYYY
# komentarze są ignorowane
https://youtu.be/ZZZZZ
```

Następnie uruchom skrypt:

```bash
python transcribe.py
```

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

## Wykrywanie FFmpeg

Skrypt automatycznie sprawdza czy FFmpeg jest zainstalowany:
- ✅ **FFmpeg znaleziony** → pełna funkcjonalność (wideo + audio)
- ⚠️ **FFmpeg nie znaleziony** → automatyczny tryb audio-only
