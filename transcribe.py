#!/usr/bin/env python3
"""
Skrypt do generowania transkrypcji z plików wideo przy użyciu OpenAI Whisper.
Opcjonalnie pobiera filmy z YouTube na podstawie pliku bulk.urls.txt.

Użycie: python transcribe.py <ścieżka_do_folderu> [--model MODEL] [--language JĘZYK]
"""

import argparse
import sys
from pathlib import Path

import whisper
from yt_dlp import YoutubeDL

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


def get_video_files(folder_path: Path) -> list[Path]:
    """Zwraca listę plików wideo w podanym folderze."""
    video_files = []
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            video_files.append(file_path)
    return sorted(video_files)


def get_videos_without_transcript(video_files: list[Path], output_dir: Path) -> list[Path]:
    """Zwraca tylko te pliki wideo, które nie mają jeszcze transkrypcji."""
    videos_to_process = []
    for video_path in video_files:
        transcript_path = output_dir / f"{video_path.stem}.transcript.txt"
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
  python transcribe.py ./videos
  python transcribe.py ./videos --model large --language en
  python transcribe.py /path/to/videos --model small

Dostępne modele: tiny, base, small, medium, large

Pobieranie z YouTube:
  Utwórz plik bulk.urls.txt w folderze docelowym z linkami (jeden na linię):
    https://youtu.be/XXXXX
    https://www.youtube.com/watch?v=YYYYY
        """
    )
    parser.add_argument(
        'folder',
        type=str,
        help='Ścieżka do folderu z plikami wideo (lub docelowego dla pobierania)'
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
        '--output-dir',
        type=str,
        default=None,
        help='Folder docelowy dla transkrypcji (domyślnie: ten sam co źródłowy)'
    )
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Pomiń pobieranie z YouTube (nawet jeśli bulk.urls.txt istnieje)'
    )

    args = parser.parse_args()

    # Walidacja/tworzenie folderu źródłowego
    folder_path = Path(args.folder).resolve()
    if not folder_path.exists():
        print(f"📁 Tworzę folder: {folder_path}")
        folder_path.mkdir(parents=True, exist_ok=True)
    if not folder_path.is_dir():
        print(f"❌ Błąd: '{folder_path}' nie jest folderem.")
        sys.exit(1)

    # Folder docelowy
    output_dir = Path(args.output_dir).resolve() if args.output_dir else folder_path
    output_dir.mkdir(parents=True, exist_ok=True)

    # === KROK 1: Pobieranie z YouTube (opcjonalne) ===
    bulk_urls_path = folder_path / BULK_URLS_FILE
    youtube_urls = load_bulk_urls(bulk_urls_path)
    
    if youtube_urls and not args.skip_download:
        print(f"🎬 Znaleziono plik {BULK_URLS_FILE} z {len(youtube_urls)} linkami")
        print("=" * 50)
        download_youtube_videos(youtube_urls, folder_path)
        print("\n" + "=" * 50)
    elif youtube_urls and args.skip_download:
        print(f"⏭️  Pomijam pobieranie z YouTube (--skip-download)")

    # === KROK 2: Znajdź pliki wideo do transkrypcji ===
    all_video_files = get_video_files(folder_path)
    video_files = get_videos_without_transcript(all_video_files, output_dir)
    
    skipped_count = len(all_video_files) - len(video_files)
    
    if not all_video_files:
        print(f"⚠️  Brak plików wideo w folderze: {folder_path}")
        print(f"   Obsługiwane rozszerzenia: {', '.join(sorted(VIDEO_EXTENSIONS))}")
        sys.exit(0)
    
    if not video_files:
        print(f"✅ Wszystkie pliki wideo ({len(all_video_files)}) mają już transkrypcje.")
        sys.exit(0)

    print(f"\n🎬 Znaleziono {len(all_video_files)} plik(ów) wideo w: {folder_path}")
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
        print(f"\n[{i}/{len(video_files)}] Przetwarzam: {video_path.name}")
        
        # Ścieżka do pliku wyjściowego
        output_filename = video_path.stem + ".transcript.txt"
        output_path = output_dir / output_filename

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
