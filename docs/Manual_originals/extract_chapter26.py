"""
PDF Page Extractor for CarMaker Chapter 26
Extracts pages 1244-1346 (User Accessible Quantities) from ReferenceManual.pdf
"""

import PyPDF2
import sys

def extract_pages(input_pdf, output_pdf, start_page, end_page):
    """
    Extract specific pages from a PDF file

    Args:
        input_pdf: Path to input PDF file
        output_pdf: Path to output PDF file
        start_page: First page to extract (1-based indexing)
        end_page: Last page to extract (1-based indexing)
    """
    try:
        # Open the input PDF
        with open(input_pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Check if requested pages are within range
            total_pages = len(pdf_reader.pages)
            print(f"Total pages in PDF: {total_pages}")

            if start_page < 1 or end_page > total_pages:
                print(f"Error: Page range {start_page}-{end_page} is out of bounds (1-{total_pages})")
                return False

            # Create a PDF writer
            pdf_writer = PyPDF2.PdfWriter()

            # Add pages to the writer (converting to 0-based index)
            for page_num in range(start_page - 1, end_page):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)

                # Progress indicator
                if (page_num - start_page + 2) % 10 == 0:
                    print(f"Processing page {page_num + 1}...")

            # Write the output PDF
            with open(output_pdf, 'wb') as output_file:
                pdf_writer.write(output_file)

            print(f"\nSuccessfully extracted pages {start_page}-{end_page}")
            print(f"Output saved to: {output_pdf}")
            print(f"Total extracted pages: {end_page - start_page + 1}")
            return True

    except FileNotFoundError:
        print(f"Error: Input file '{input_pdf}' not found")
        return False
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    # Configuration
    INPUT_PDF = "ReferenceManual.pdf"
    OUTPUT_PDF = "Chapter26_UserAccessibleQuantities.pdf"
    START_PAGE = 1244  # Chapter 26 start
    END_PAGE = 1346    # Chapter 26 end

    print("CarMaker Manual - Chapter 26 Extractor")
    print("=" * 50)
    print(f"Input file: {INPUT_PDF}")
    print(f"Extracting pages: {START_PAGE}-{END_PAGE}")
    print(f"Output file: {OUTPUT_PDF}")
    print("=" * 50)

    # Extract the pages
    success = extract_pages(INPUT_PDF, OUTPUT_PDF, START_PAGE, END_PAGE)

    if success:
        print("\n✓ Extraction completed successfully!")
    else:
        print("\n✗ Extraction failed!")
        sys.exit(1)