#!/usr/bin/env python3
"""
Skrypt do generowania transkrypcji z plików wideo przy użyciu OpenAI Whisper.
Opcjonalnie pobiera filmy z YouTube na podstawie pliku bulk.urls.txt.

Użycie: python transcribe.py [--model MODEL] [--language JĘZYK]
"""

import argparse
import sys
from pathlib import Path

import whisper
from yt_dlp import YoutubeDL

# Domyślny folder workspace
VIDEOS_DIR = Path(__file__).parent / "videos"

# Obsługiwane rozszerzenia plików wideo
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v', '.mpeg', '.mpg'}

# Nazwa pliku z linkami do YouTube
BULK_URLS_FILE = "bulk.urls.txt"


def download_youtube_videos(urls: list[str], output_dir: Path) -> list[Path]:
    """Pobiera filmy z YouTube i zwraca listę pobranych plików."""
    downloaded_files = []
    
    opts = {
        'format': 'best',
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
    }
    
    with YoutubeDL(opts) as ytdl:
        for i, url in enumerate(urls, 1):
            url = url.strip()
            if not url:
                continue
                
            print(f"\n[{i}/{len(urls)}] 📥 Pobieram: {url}")
            try:
                # Pobierz info o filmie
                info = ytdl.extract_info(url, download=False)
                if info is None:
                    print(f"  ❌ Nie można pobrać informacji o filmie: {url}")
                    continue
                    
                title = info.get('title', 'video')
                ext = info.get('ext', 'mp4')
                expected_path = output_dir / f"{title}.{ext}"
                
                # Sprawdź czy transkrypcja już istnieje
                transcript_path = output_dir / f"{title}.transcript.txt"
                if transcript_path.exists():
                    print(f"  ⏭️  Pomijam pobieranie (transkrypcja już istnieje): {title}")
                    continue
                
                # Sprawdź czy plik już istnieje
                if expected_path.exists():
                    print(f"  ⏭️  Plik już istnieje: {expected_path.name}")
                    downloaded_files.append(expected_path)
                    continue
                
                # Pobierz film
                ytdl.download([url])
                
                # Znajdź pobrany plik (nazwa może być sanitized)
                for file_path in output_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                        # Sprawdź czy to nowy plik (porównaj z expected)
                        if title.lower() in file_path.stem.lower() or file_path == expected_path:
                            if file_path not in downloaded_files:
                                downloaded_files.append(file_path)
                                print(f"  ✅ Pobrano: {file_path.name}")
                                break
                else:
                    # Fallback - szukaj plików z odpowiednim rozszerzeniem
                    if expected_path.exists():
                        downloaded_files.append(expected_path)
                        print(f"  ✅ Pobrano: {expected_path.name}")
                        
            except Exception as e:
                print(f"  ❌ Błąd pobierania: {e}")
    
    return downloaded_files


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


def get_video_files_recursive(folder_path: Path) -> list[Path]:
    """Zwraca listę plików wideo rekursywnie w podanym folderze i podfolderach."""
    video_files = []
    for file_path in folder_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            video_files.append(file_path)
    return sorted(video_files)


def get_videos_without_transcript(video_files: list[Path]) -> list[Path]:
    """Zwraca tylko te pliki wideo, które nie mają jeszcze transkrypcji (obok pliku wideo)."""
    videos_to_process = []
    for video_path in video_files:
        # Transkrypcja jest zapisywana obok pliku wideo
        transcript_path = video_path.parent / f"{video_path.stem}.transcript.txt"
        if not transcript_path.exists():
            videos_to_process.append(video_path)
    return videos_to_process


def transcribe_video(model, video_path: Path, language: str) -> str:
    """Transkrybuje plik wideo i zwraca tekst."""
    print(f"  📝 Transkrybuję: {video_path.name}")
    result = model.transcribe(str(video_path), language=language)
    return result["text"]


def save_transcript(transcript: str, output_path: Path) -> None:
    """Zapisuje transkrypcję do pliku."""
    output_path.write_text(transcript, encoding='utf-8')
    print(f"  ✅ Zapisano: {output_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Generuj transkrypcje z plików wideo przy użyciu Whisper.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python transcribe.py
  python transcribe.py --model large --language en
  python transcribe.py --skip-download

Dostępne modele: tiny, base, small, medium, large

Pobieranie z YouTube:
  Utwórz plik videos/bulk.urls.txt z linkami (jeden na linię):
    https://youtu.be/XXXXX
    https://www.youtube.com/watch?v=YYYYY

Transkrypcje są zapisywane obok plików wideo (rekursywnie).
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

    args = parser.parse_args()

    # Sprawdź/utwórz folder videos/
    if not VIDEOS_DIR.exists():
        VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"📁 Utworzono folder workspace: {VIDEOS_DIR}")
        print()
        print("ℹ️  Folder videos/ jest pusty. Aby rozpocząć:")
        print("   1. Umieść pliki wideo w folderze videos/")
        print("   2. Lub utwórz plik videos/bulk.urls.txt z linkami YouTube")
        print()
        print("   Następnie uruchom skrypt ponownie: python transcribe.py")
        sys.exit(0)

    print(f"📂 Workspace: {VIDEOS_DIR}")

    # === KROK 1: Pobieranie z YouTube (opcjonalne) ===
    bulk_urls_path = VIDEOS_DIR / BULK_URLS_FILE
    youtube_urls = load_bulk_urls(bulk_urls_path)
    
    if youtube_urls and not args.skip_download:
        print(f"🎬 Znaleziono plik {BULK_URLS_FILE} z {len(youtube_urls)} linkami")
        print("=" * 50)
        download_youtube_videos(youtube_urls, VIDEOS_DIR)
        print("\n" + "=" * 50)
    elif youtube_urls and args.skip_download:
        print(f"⏭️  Pomijam pobieranie z YouTube (--skip-download)")

    # === KROK 2: Znajdź pliki wideo rekursywnie ===
    all_video_files = get_video_files_recursive(VIDEOS_DIR)
    video_files = get_videos_without_transcript(all_video_files)
    
    skipped_count = len(all_video_files) - len(video_files)
    
    if not all_video_files:
        print(f"⚠️  Brak plików wideo w folderze: {VIDEOS_DIR}")
        print(f"   Obsługiwane rozszerzenia: {', '.join(sorted(VIDEO_EXTENSIONS))}")
        print()
        print("ℹ️  Aby rozpocząć:")
        print("   1. Umieść pliki wideo w folderze videos/ (lub podfolderach)")
        print("   2. Lub utwórz plik videos/bulk.urls.txt z linkami YouTube")
        sys.exit(0)
    
    if not video_files:
        print(f"✅ Wszystkie pliki wideo ({len(all_video_files)}) mają już transkrypcje.")
        sys.exit(0)

    print(f"\n🎬 Znaleziono {len(all_video_files)} plik(ów) wideo (rekursywnie)")
    print(f"   📝 Do transkrypcji: {len(video_files)}")
    print(f"   ⏭️  Już z transkrypcją: {skipped_count}")
    
    print(f"\n🤖 Ładuję model Whisper: {args.model}")

    # Załaduj model
    model = whisper.load_model(args.model)

    print(f"🌐 Język: {args.language}")
    print("-" * 50)

    # === KROK 3: Transkrypcja ===
    success_count = 0
    error_count = 0

    for i, video_path in enumerate(video_files, 1):
        # Pokaż relatywną ścieżkę do videos/
        relative_path = video_path.relative_to(VIDEOS_DIR)
        print(f"\n[{i}/{len(video_files)}] Przetwarzam: {relative_path}")
        
        # Ścieżka do pliku wyjściowego (obok pliku wideo)
        output_path = video_path.parent / f"{video_path.stem}.transcript.txt"

        try:
            transcript = transcribe_video(model, video_path, args.language)
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
