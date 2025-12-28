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
    ├── video1.mp4
    ├── video1.transcript.txt
    └── ...
```

> 💡 **Tip:** Folder `videos/` to idealne miejsce workspace skryptu - umieść tam pliki wideo lub `bulk.urls.txt` z linkami YouTube. Folder `venv/` zawiera wirtualne środowisko Python. Oba foldery są ignorowane przez git.

## Użycie

### Podstawowe użycie

```bash
# Transkrypcja plików wideo z folderu videos/ (model medium, język polski)
python transcribe.py ./videos

# Z wyborem modelu i języka
python transcribe.py ./videos --model large --language en

# Zapis transkrypcji do innego folderu
python transcribe.py ./videos --output-dir /ścieżka/do/transkrypcji
```

### Pobieranie z YouTube (bulk)

Utwórz plik `bulk.urls.txt` w folderze docelowym z linkami do filmów (jeden na linię):

```
https://youtu.be/XXXXX
https://www.youtube.com/watch?v=YYYYY
# komentarze są ignorowane
https://youtu.be/ZZZZZ
```

Następnie uruchom skrypt:

```bash
python transcribe.py ./videos
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
| `--output-dir` | folder źródłowy | Folder docelowy dla transkrypcji |
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

Transkrypcje są zapisywane z rozszerzeniem `.transcript.txt`:

```
video.mp4 → video.transcript.txt
nagranie.mkv → nagranie.transcript.txt
```

## Logika pomijania

Skrypt inteligentnie pomija:
- ⏭️ Pobieranie filmów z YouTube, które mają już transkrypcję
- ⏭️ Transkrypcję filmów, które mają już plik `.transcript.txt`

Dzięki temu można wielokrotnie uruchamiać skrypt bez ponownego przetwarzania.
