# Video Transcript Generator

Skrypt do automatycznego generowania transkrypcji z plików wideo przy użyciu OpenAI Whisper.  
Opcjonalnie pobiera filmy z YouTube przy użyciu yt-dlp.

## Wymagania systemowe

```bash
# FFmpeg (wymagany przez Whisper i yt-dlp)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
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
└── videos/             # Workspace - miejsce na filmy i transkrypcje (ignorowane przez git)
    ├── bulk.urls.txt   # Opcjonalny plik z linkami YouTube
    ├── subfolder/      # Podfoldery są obsługiwane (rekursywnie)
    │   ├── video2.mp4
    │   └── video2.transcript.txt
    ├── video1.mp4
    ├── video1.transcript.txt
    └── ...
```

> 💡 **Tip:** Folder `videos/` to domyślny workspace skryptu - umieść tam pliki wideo lub `bulk.urls.txt` z linkami YouTube. Skrypt przeszukuje folder rekursywnie, więc możesz organizować filmy w podfolderach. Folder `venv/` zawiera wirtualne środowisko Python. Oba foldery są ignorowane przez git.

## Użycie

### Podstawowe użycie

```bash
# Transkrypcja plików wideo z folderu videos/ (model medium, język polski)
python transcribe.py

# Z wyborem modelu i języka
python transcribe.py --model large --language en

# Pomiń pobieranie z YouTube
python transcribe.py --skip-download
```

Skrypt automatycznie:
- Używa folderu `videos/` jako workspace (tworzy go jeśli nie istnieje)
- Przeszukuje folder **rekursywnie** (włącznie z podfolderami)
- Zapisuje transkrypcje **obok plików wideo** (w tej samej lokalizacji)

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
1. Pobierze filmy z YouTube (jeśli `bulk.urls.txt` istnieje)
2. Pominie pobieranie filmów, które mają już transkrypcję
3. Wygeneruje transkrypcje dla wszystkich filmów bez transkrypcji

### Opcje

| Opcja | Domyślnie | Opis |
|-------|-----------|------|
| `--model` | `medium` | Model Whisper: tiny, base, small, medium, large |
| `--language` | `pl` | Język audio |
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

`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.flv`, `.wmv`, `.m4v`, `.mpeg`, `.mpg`

## Pliki wyjściowe

Transkrypcje są zapisywane **obok plików wideo** z rozszerzeniem `.transcript.txt`:

```
videos/video.mp4 → videos/video.transcript.txt
videos/kurs/lekcja1.mkv → videos/kurs/lekcja1.transcript.txt
```

## Logika pomijania

Skrypt inteligentnie pomija:
- ⏭️ Pobieranie filmów z YouTube, które mają już transkrypcję
- ⏭️ Transkrypcję filmów, które mają już plik `.transcript.txt`

Dzięki temu można wielokrotnie uruchamiać skrypt bez ponownego przetwarzania.
