# Jesus, please let this code work
# import stuff
import sys
from pathlib import Path
# Jesus, please let this code work
# pdfplumber importer and checker. You shouldn't need this if you're using the Deployed Program, but it's in here encase you're building from Source, and don't have pdfplumber installed.
try:
    import pdfplumber
except ImportError:
    print("ERROR: Extreme skill issue detected, you don't have pdfplumber installed.")
    print("You can fix this skill issue by going into your 'terminal' or 'command prompt' or whatever you use, and type: 'pip install pdfplumber'. That is assuming you have Python, and if you don't, then you'll need to install Python.")
    sys.exit(1)
    # Jesus, please let this code work
    # Greek and Coptic Character Checker. The modern Coptic, I.E Egyptian, is largly based on the Greek Alphabet, so there is literally no reason to not include it. It would be more work to exclude it.
def IsGreek(ch: str) -> bool:
    """Return True if the character is Greek (including polytonic)."""
    code = ord(ch)
    # Greek & Coptic
    if 0x0370 <= code <= 0x03FF:
        return True
    # Greek Extended (polytonic)
    if 0x1F00 <= code <= 0x1FFF:
        return True
    return False
# Jesus, please let this code work
# Hebrew Character Checker. Also grabs Niqqud and other diacritics.
def IsHebrew(ch: str) -> bool:
    """Return True if the character is Hebrew."""
    code = ord(ch)
    return 0x0590 <= code <= 0x05FF
# Jesus, please let this code work
# Hebrew Character Flipper. If those code isn't included, the Hebrew text will be backwards. That is because this program reads left-to-right, but Hebrew is right-to-left. This ensures that the Hebrew characters will be in their correct ordering.
def HebrewReverser(token: str) -> str:
    """
    Reverse just the Hebrew part of a token, keeping any punctuation
    at the edges in place. E.g. 'תישארב,' -> ',בראשית'
    """
    start = 0
    end = len(token)
    # Skip non-Hebrew at the start
    while start < end and not IsHebrew(token[start]):
        start += 1
    # Skip non-Hebrew at the end
    while end > start and not IsHebrew(token[end - 1]):
        end -= 1
    # No Hebrew in this token
    if start >= end:
        return token
    hebrew_part = token[start:end][::-1]
    return token[:start] + hebrew_part + token[end:]
# Jesus, please let this code work.
# This spit of code is what keeps the Hebrew in its correct word-ordering, while the previous function makes sure the characters in each word are in the correct order.
def HebrewLineFixer(line: str) -> str:
    """
    For one line, reverse each Hebrew token, but keep the order of words.
    So:
        'תישארב ארב םיהלא'
    becomes:
        'בראשית ברא אלהים'
    """
    tokens = line.split(" ")
    fixed_tokens = []
    for t in tokens:
        if any(IsHebrew(ch) for ch in t):
            fixed_tokens.append(HebrewReverser(t))
        else:
            fixed_tokens.append(t)
    return " ".join(fixed_tokens)
# Jesus, please let this code work
# Actual extraction function. Reads the PDF(s), pulls out Greek and Hebrew, and writes to text files.
def TextExtractor(pdf_path: Path) -> None:
    """Read ONE PDF, pull out Greek and Hebrew into text files next to it."""
    print(f"\n[INFO] === Processing: {pdf_path.name} ===")
    if not pdf_path.exists():
        print(f"[ERROR] File not found: {pdf_path}")
        return
    GreekChars = []
    HebrewChars = []
    # Open the PDF
    with pdfplumber.open(pdf_path) as pdf:
        print(f"[INFO] Pages in PDF: {len(pdf.pages)}")
        for page_number, page in enumerate(pdf.pages, start=1):
            print(f"[INFO] Reading page {page_number} ...")
            text = page.extract_text() or ""
            for ch in text:
                # Keep line breaks so text isn't one giant line
                if ch in ("\n", "\r"):
                    GreekChars.append("\n")
                    HebrewChars.append("\n")
                    continue

                if IsGreek(ch):
                    GreekChars.append(ch)
                elif IsHebrew(ch):
                    HebrewChars.append(ch)
                # Without this code, the program try to pull ALL characters, which would make the program nonfunctional.
    # Turn character lists into full strings
    GreekText = "".join(GreekChars)
    HebrewText = "".join(HebrewChars)
    # Detect if there is *real* content (ignoring just newlines/whitespace)
    HasGreek = bool(GreekText.strip())
    HasRawHebrew = bool(HebrewText.strip())
    # Fix Hebrew only if we actually found any
    if HasRawHebrew:
        lines = HebrewText.splitlines()
        fixed_lines = [HebrewLineFixer(line) for line in lines]
        fixed_hebrew_text = "\n".join(fixed_lines)
        HasHebrew = bool(fixed_hebrew_text.strip())
    else:
        fixed_hebrew_text = ""
        HasHebrew = False
    if not HasGreek and not HasHebrew:
        print("[WARN] No Greek or Hebrew characters found in this PDF.")
        return
    # Build output file names based on THIS PDF's name
    BaseName = pdf_path.stem
    if HasGreek:
        GreekOut = pdf_path.with_name(f"{BaseName}_greek.txt") # as an aside, "Greek Out" is a great band name.
        with open(GreekOut, "w", encoding="utf-8") as g:
            g.write(GreekText)
        print(f"[INFO] Greek text  -> {GreekOut.name}")
    else:
        print("[INFO] No Greek text found; skipping Greek output file.")
    if HasHebrew:
        HebrewOut = pdf_path.with_name(f"{BaseName}_hebrew.txt") # Hebrew Out isn't nearlly as good as Greek Out :(
        with open(HebrewOut, "w", encoding="utf-8") as h:
            h.write(fixed_hebrew_text)
        print(f"[INFO] Hebrew text -> {HebrewOut.name}")
    else:
        print("[INFO] No Hebrew text found; skipping Hebrew output file.")

    print("[INFO] Done for this PDF.")
# Jesus, please let this code work
# Process either a single file or all PDFs in a folder. It's what allows the program to work on multiple PDFs at once.
def process_target(target: Path) -> None:
    """
    If target is a file: process that one PDF.
    If target is a folder: process ALL *.pdf files in that folder.
    """
    if target.is_file():
        if target.suffix.lower() == ".pdf":
            TextExtractor(target)
        else:
            print(f"[ERROR] {target} is a file but not a .pdf")
        return
    if target.is_dir():
        pdfs = sorted(target.glob("*.pdf"))
        if not pdfs:
            print(f"[WARN] No PDF files found in folder: {target}")
            return
        print(f"[INFO] Found {len(pdfs)} PDF file(s) in {target}")
        for pdf in pdfs:
            TextExtractor(pdf)
        print("\n[INFO] All PDFs processed.")
        return
    print(f"[ERROR] Path does not exist: {target}")
# Jesus, please let this code work
# Main. Doesn't really do much, but without it, the program doesn't work.
if __name__ == "__main__":
    print("[DEBUG] sys.argv:", sys.argv)
    # Usage:
    #   python GreekHebrewTextExtractor.py          -> process current folder
    #   python GreekHebrewTextExtractor.py path     -> process that file or folder
    if len(sys.argv) == 1:
        # No argument: use current directory
        target_path = Path(".").resolve()
    elif len(sys.argv) == 2:
        target_path = Path(sys.argv[1]).resolve()
    else:
        print("Usage:")
        print("  python GreekHebrewTextExtractor.py")
        print("  python GreekHebrewTextExtractor.py path_to_pdf_or_folder")
        sys.exit(1)

    print(f"[INFO] Target: {target_path}")
    process_target(target_path)
# Psalm 16, my favorite Psalm:
    # 1.) Preserve me, O God, for in you I take refuge.
    # 2.) I say to the Lord, “You are my Lord; I have no good apart from you.”
    # 3.) As for the saints in the land, they are the excellent ones, in whom is all my delight.
    # 4.) The sorrows of those who run after another god shall multiply; their drink offerings of blood I will not pour out or take their names on my lips.
    # 5.) The Lord is my chosen portion and my cup; you hold my lot.
    # 6.) The lines have fallen for me in pleasant places; indeed, I have a beautiful inheritance.
    # 7.) I bless the Lord who gives me counsel; in the night also my heart instructs me.
    # 8.) I have set the Lord always before me; because he is at my right hand, I shall not be shaken.
    # 9.) Therefore my heart is glad, and my whole being rejoices; my flesh also dwells secure.
    # 10.) For you will not abandon my soul to Sheol, or let your holy one see corruption.
    # 11.) You make known to me the path of life; in your presence there is fullness of joy; at your right hand are pleasures forevermore.
# Jesus came into this world to save sinners, of which everyone is. You are not thrown into the Lake of Fire for your sins, you are thrown in because of your refusal to accept God's remedy. Repent to the יהוה, accept Jesus into your life, and let the splattering of his blood make your sins as white as snow. If he did it to me, with all my faults and foibles, he can do it to you.