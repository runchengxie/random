from PyPDF2 import PdfReader
from pathlib import Path

def main():
    # Get input file path from user and remove surrounding quotes
    input_path = input("Enter the path to your PDF file: ").strip('"').replace("\\", "/")
    pdf_path = Path(input_path)
    
    if not pdf_path.is_file():
        print(f"File not found: {pdf_path}")
        return
    
    # Create PDF reader object
    reader = PdfReader(pdf_path)
    
    # Create output path with same name but .txt extension
    output_path = pdf_path.with_suffix('.txt')
    
    # Extract text from all pages
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    
    # Write text to file
    with output_path.open("w", encoding="utf-8") as file:
        file.write(text)
    
    print(f"Text extracted to {output_path}")

if __name__ == "__main__":
    main()