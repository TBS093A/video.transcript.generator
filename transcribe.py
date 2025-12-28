#!/usr/bin/env python3
"""
Skrypt do generowania transkrypcji z plików wideo/audio przy użyciu OpenAI Whisper.
Opcjonalnie pobiera filmy z YouTube na podstawie pliku bulk.urls.txt.

Użycie: python transcribe.py [--model MODEL] [--language JĘZYK] [--audio-only]
"""

import argparse
import shutil
import sys
from pathlib import Path

import whisper
from yt_dlp import YoutubeDL

# Domyślny folder workspace
VIDEOS_DIR = Path(__file__).parent / "videos"

# Obsługiwane rozszerzenia plików
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v', '.mpeg', '.mpg'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.opus', '.aac', '.wma', '.webm'}
ALL_MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS

# Nazwa pliku z linkami do YouTube
BULK_URLS_FILE = "bulk.urls.txt"


def check_ffmpeg() -> bool:
    """Sprawdza czy ffmpeg jest zainstalowany i dostępny w PATH."""
    return shutil.which('ffmpeg') is not None


def download_youtube_content(urls: list[str], output_dir: Path, audio_only: bool = False) -> None:
    """Pobiera treści z YouTube (wideo lub audio). Używa archiwum do pomijania już pobranych."""
    
    # Archiwum pobranych plików - zapobiega ponownemu pobieraniu
    download_archive = str(output_dir / '.downloaded_archive.txt')
    
    # Szablon nazwy pliku:
    # - Dla playlist: NazwaPlaylisty/001 - Tytuł.ext
    # - Dla pojedynczych: Tytuł.ext
    common_opts = {
        'paths': {'home': str(output_dir)},
        'outtmpl': {
            'default': '%(playlist_title&{}/|)s%(playlist_index&{:03d} - |)s%(title)s.%(ext)s',
        },
        'quiet': False,
        'no_warnings': False,
        'download_archive': download_archive,
        'ignoreerrors': True,  # Kontynuuj mimo błędów pojedynczych filmów
    }
    
    if audio_only:
        # Tryb audio - pobieraj tylko audio w oryginalnym formacie (webm/m4a)
        opts = {
            **common_opts,
            'format': 'bestaudio/best',
        }
        file_type = "audio"
    else:
        # Tryb video - preferuj webm, fallback do best
        opts = {
            **common_opts,
            'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best',
        }
        file_type = "wideo"
    
    with YoutubeDL(opts) as ytdl:
        for i, url in enumerate(urls, 1):
            url = url.strip()
            if not url:
                continue
                
            print(f"\n[{i}/{len(urls)}] 📥 Pobieram ({file_type}): {url}")
            try:
                # Pobierz (yt-dlp automatycznie pomija już pobrane dzięki download_archive)
                ytdl.download([url])
            except Exception as e:
                print(f"  ❌ Błąd pobierania: {e}")


def load_bulk_urls(file_path: Path) -> list[str]:
    """Wczytuje linki z pliku bulk.urls.txt."""
    if not file_path.exists():
        return []
    
    urls = []
    content = file_path.read_text(encoding='utf-8')
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):  # Ignoruj puste linie i komentarze
            urls.append(line)
    return urls


def get_media_files_recursive(folder_path: Path, audio_only: bool = False) -> list[Path]:
    """Zwraca listę plików media rekursywnie w podanym folderze i podfolderach."""
    if audio_only:
        extensions = AUDIO_EXTENSIONS
    else:
        extensions = ALL_MEDIA_EXTENSIONS
    
    media_files = []
    for file_path in folder_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            media_files.append(file_path)
    return sorted(media_files)


def get_files_without_transcript(media_files: list[Path]) -> list[Path]:
    """Zwraca tylko te pliki media, które nie mają jeszcze transkrypcji."""
    files_to_process = []
    for media_path in media_files:
        transcript_path = media_path.parent / f"{media_path.stem}.transcript.txt"
        if not transcript_path.exists():
            files_to_process.append(media_path)
    return files_to_process


def transcribe_media(model, media_path: Path, language: str) -> str:
    """Transkrybuje plik wideo/audio i zwraca tekst."""
    print(f"  📝 Transkrybuję: {media_path.name}")
    result = model.transcribe(str(media_path), language=language)
    return result["text"]


def save_transcript(transcript: str, output_path: Path) -> None:
    """Zapisuje transkrypcję do pliku."""
    output_path.write_text(transcript, encoding='utf-8')
    print(f"  ✅ Zapisano: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Generuj transkrypcje z plików wideo/audio przy użyciu Whisper.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python transcribe.py
  python transcribe.py --model large --language en
  python transcribe.py --audio-only
  python transcribe.py --skip-download

Dostępne modele: tiny, base, small, medium, large

Pobieranie z YouTube:
  Utwórz plik videos/bulk.urls.txt z linkami (jeden na linię):
    https://youtu.be/XXXXX
    https://www.youtube.com/watch?v=YYYYY

Transkrypcje są zapisywane obok plików media (rekursywnie).

Tryb audio (--audio-only):
  - Pobiera audio zamiast wideo z YouTube (mniejsze pliki)
  - Przetwarza tylko pliki audio (.mp3, .wav, .m4a, itp.)

Wymagania: FFmpeg musi być zainstalowany (używany przez Whisper)
        """
    )
    parser.add_argument(
        '--model',
        type=str,
        default='medium',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Model Whisper do użycia (domyślnie: medium)'
    )
    parser.add_argument(
        '--language',
        type=str,
        default='pl',
        help='Język audio (domyślnie: pl - polski)'
    )
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Pomiń pobieranie z YouTube (nawet jeśli bulk.urls.txt istnieje)'
    )
    parser.add_argument(
        '--audio-only',
        action='store_true',
        help='Używaj tylko plików audio (pobieraj audio z YouTube, przetwarzaj tylko audio)'
    )

    args = parser.parse_args()

    # Sprawdź ffmpeg - jest WYMAGANY przez Whisper
    if not check_ffmpeg():
        print("❌ FFmpeg nie został znaleziony w systemie!")
        print()
        print("   FFmpeg jest wymagany przez Whisper do przetwarzania plików audio/video.")
        print()
        print("   Aby zainstalować FFmpeg:")
        print("   • macOS: brew install ffmpeg")
        print("   • Ubuntu/Debian: sudo apt install ffmpeg")
        print("   • Windows: choco install ffmpeg  lub  winget install ffmpeg")
        print()
        print("   Po instalacji uruchom skrypt ponownie.")
        sys.exit(1)
    
    print("✅ FFmpeg znaleziony")
    
    audio_only = args.audio_only
    if audio_only:
        print("🎵 Tryb: audio-only")
        extensions_info = ', '.join(sorted(AUDIO_EXTENSIONS))
    else:
        print("🎬 Tryb: wideo + audio")
        extensions_info = ', '.join(sorted(ALL_MEDIA_EXTENSIONS))

    # Sprawdź/utwórz folder videos/
    if not VIDEOS_DIR.exists():
        VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"\n📁 Utworzono folder workspace: {VIDEOS_DIR}")
        print()
        print("ℹ️  Folder videos/ jest pusty. Aby rozpocząć:")
        if audio_only:
            print("   1. Umieść pliki audio w folderze videos/")
        else:
            print("   1. Umieść pliki wideo/audio w folderze videos/")
        print("   2. Lub utwórz plik videos/bulk.urls.txt z linkami YouTube")
        print()
        print("   Następnie uruchom skrypt ponownie: python transcribe.py")
        sys.exit(0)

    print(f"📂 Workspace: {VIDEOS_DIR}")

    # === KROK 1: Pobieranie z YouTube (opcjonalne) ===
    bulk_urls_path = VIDEOS_DIR / BULK_URLS_FILE
    youtube_urls = load_bulk_urls(bulk_urls_path)
    
    if youtube_urls and not args.skip_download:
        print(f"\n🎬 Znaleziono plik {BULK_URLS_FILE} z {len(youtube_urls)} linkami")
        print("=" * 50)
        download_youtube_content(youtube_urls, VIDEOS_DIR, audio_only=audio_only)
        print("\n" + "=" * 50)
    elif youtube_urls and args.skip_download:
        print(f"⏭️  Pomijam pobieranie z YouTube (--skip-download)")

    # === KROK 2: Znajdź pliki media rekursywnie ===
    all_media_files = get_media_files_recursive(VIDEOS_DIR, audio_only=audio_only)
    media_files = get_files_without_transcript(all_media_files)
    
    skipped_count = len(all_media_files) - len(media_files)
    
    if not all_media_files:
        print(f"\n⚠️  Brak plików media w folderze: {VIDEOS_DIR}")
        print(f"   Obsługiwane rozszerzenia: {extensions_info}")
        print()
        print("ℹ️  Aby rozpocząć:")
        if audio_only:
            print("   1. Umieść pliki audio w folderze videos/ (lub podfolderach)")
        else:
            print("   1. Umieść pliki wideo/audio w folderze videos/ (lub podfolderach)")
        print("   2. Lub utwórz plik videos/bulk.urls.txt z linkami YouTube")
        sys.exit(0)
    
    if not media_files:
        print(f"\n✅ Wszystkie pliki media ({len(all_media_files)}) mają już transkrypcje.")
        sys.exit(0)

    print(f"\n🎬 Znaleziono {len(all_media_files)} plik(ów) media (rekursywnie)")
    print(f"   📝 Do transkrypcji: {len(media_files)}")
    print(f"   ⏭️  Już z transkrypcją: {skipped_count}")
    
    print(f"\n🤖 Ładuję model Whisper: {args.model}")

    # Załaduj model
    model = whisper.load_model(args.model)

    print(f"🌐 Język: {args.language}")
    print("-" * 50)

    # === KROK 3: Transkrypcja ===
    success_count = 0
    error_count = 0

    for i, media_path in enumerate(media_files, 1):
        # Pokaż relatywną ścieżkę do videos/
        relative_path = media_path.relative_to(VIDEOS_DIR)
        print(f"\n[{i}/{len(media_files)}] Przetwarzam: {relative_path}")
        
        # Ścieżka do pliku wyjściowego (obok pliku media)
        output_path = media_path.parent / f"{media_path.stem}.transcript.txt"

        try:
            transcript = transcribe_media(model, media_path, args.language)
            save_transcript(transcript, output_path)
            success_count += 1
        except Exception as e:
            print(f"  ❌ Błąd podczas transkrypcji: {e}")
            error_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Podsumowanie transkrypcji:")
    print(f"   ✅ Sukces: {success_count}")
    print(f"   ❌ Błędy: {error_count}")
    print(f"   ⏭️  Pominięto (już istniały): {skipped_count}")


if __name__ == "__main__":
    main()
