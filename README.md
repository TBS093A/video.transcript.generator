# Video Transcript Generator

Skrypt do automatycznego generowania transkrypcji z plików wideo przy użyciu OpenAI Whisper.

## Wymagania systemowe

```bash
# FFmpeg (wymagany przez Whisper)
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

```bash
# Podstawowe użycie (model medium, język polski)
python transcribe.py /ścieżka/do/folderu/z/video

# Z wyborem modelu i języka
python transcribe.py /ścieżka/do/folderu --model large --language en

# Zapis transkrypcji do innego folderu
python transcribe.py /ścieżka/do/video --output-dir /ścieżka/do/transkrypcji
```

## Dostępne modele

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

