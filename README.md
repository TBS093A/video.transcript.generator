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
pip install -r requirements.txt
```

## Użycie

### Podstawowe użycie

```bash
# Transkrypcja plików wideo z folderu (model medium, język polski)
python transcribe.py /ścieżka/do/folderu/z/video

# Z wyborem modelu i języka
python transcribe.py /ścieżka/do/folderu --model large --language en

# Zapis transkrypcji do innego folderu
python transcribe.py /ścieżka/do/video --output-dir /ścieżka/do/transkrypcji
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
python transcribe.py /ścieżka/do/folderu
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
