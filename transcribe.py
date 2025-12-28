#!/usr/bin/env python3
"""
Skrypt do generowania transkrypcji z plików wideo przy użyciu OpenAI Whisper.
Użycie: python transcribe.py <ścieżka_do_folderu> [--model MODEL] [--language JĘZYK]
"""

import argparse
import sys
from pathlib import Path

import whisper

# Obsługiwane rozszerzenia plików wideo
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v', '.mpeg', '.mpg'}


def get_video_files(folder_path: Path) -> list[Path]:
    """Zwraca listę plików wideo w podanym folderze."""
    video_files = []
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            video_files.append(file_path)
    return sorted(video_files)


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
        """
    )
    parser.add_argument(
        'folder',
        type=str,
        help='Ścieżka do folderu z plikami wideo'
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

    args = parser.parse_args()

    # Walidacja folderu źródłowego
    folder_path = Path(args.folder).resolve()
    if not folder_path.exists():
        print(f"❌ Błąd: Folder '{folder_path}' nie istnieje.")
        sys.exit(1)
    if not folder_path.is_dir():
        print(f"❌ Błąd: '{folder_path}' nie jest folderem.")
        sys.exit(1)

    # Folder docelowy
    output_dir = Path(args.output_dir).resolve() if args.output_dir else folder_path
    output_dir.mkdir(parents=True, exist_ok=True)

    # Znajdź pliki wideo
    video_files = get_video_files(folder_path)
    if not video_files:
        print(f"⚠️  Brak plików wideo w folderze: {folder_path}")
        print(f"   Obsługiwane rozszerzenia: {', '.join(sorted(VIDEO_EXTENSIONS))}")
        sys.exit(0)

    print(f"🎬 Znaleziono {len(video_files)} plik(ów) wideo w: {folder_path}")
    print(f"🤖 Ładuję model Whisper: {args.model}")

    # Załaduj model
    model = whisper.load_model(args.model)

    print(f"🌐 Język: {args.language}")
    print("-" * 50)

    # Przetwarzaj każdy plik
    success_count = 0
    error_count = 0

    for i, video_path in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Przetwarzam: {video_path.name}")
        
        # Ścieżka do pliku wyjściowego
        output_filename = video_path.stem + ".transcript.txt"
        output_path = output_dir / output_filename

        # Sprawdź czy transkrypcja już istnieje
        if output_path.exists():
            print(f"  ⏭️  Pomijam (transkrypcja już istnieje): {output_filename}")
            continue

        try:
            transcript = transcribe_video(model, video_path, args.language)
            save_transcript(transcript, output_path)
            success_count += 1
        except Exception as e:
            print(f"  ❌ Błąd podczas transkrypcji: {e}")
            error_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Podsumowanie:")
    print(f"   ✅ Sukces: {success_count}")
    print(f"   ❌ Błędy: {error_count}")
    print(f"   ⏭️  Pominięto: {len(video_files) - success_count - error_count}")


if __name__ == "__main__":
    main()

