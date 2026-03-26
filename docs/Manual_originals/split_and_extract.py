
import PyPDF2
import os

def extract_content_by_ranges(pdf_path, ranges):
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found.")
        return

    try:
        reader = PyPDF2.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"Total pages: {total_pages}")

        for name, (start, end) in ranges.items():
            txt_filename = f"UAQ_{name}.txt"
            pdf_filename = f"UAQ_{name}.pdf"
            print(f"Processing {name} (Pages {start}-{end})...")
            
            # Convert 1-based page numbers to 0-based indices
            start_idx = start - 1
            end_idx = end - 1
            
            if start_idx < 0: start_idx = 0
            if end_idx >= total_pages: end_idx = total_pages - 1

            # Extract Text
            text_content = []
            # Create PDF Writer for splitting
            writer = PyPDF2.PdfWriter()

            for i in range(start_idx, end_idx + 1):
                try:
                    page = reader.pages[i]
                    # Add to PDF writer
                    writer.add_page(page)
                    
                    # Extract text
                    page_text = page.extract_text()
                    text_content.append(f"--- Page {i+1} ---\n{page_text}\n")
                except Exception as e:
                    print(f"Error processing page {i+1}: {e}")

            # Save Text
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write("".join(text_content))
            print(f"Saved text to {txt_filename}")

            # Save PDF
            with open(pdf_filename, 'wb') as f:
                writer.write(f)
            print(f"Saved PDF to {pdf_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pdf_file = "Chapter26_UserAccessibleQuantities.pdf"
    
    # User defined ranges (1-based, inclusive)
    topic_ranges = {
        "01_General_Control": (2, 13),
        "02_Car": (14, 25),
        "03_Suspension": (25, 44),
        "04_Suspension_Tire_Brake": (45, 55),
        "05_Powertrain": (56, 68),
        "06_Sensor_Part1": (69, 81),
        "06_Sensor_Part2": (82, 90),
        "07_Trailer": (91, 97),
        "08_Traffic": (98, 102)
    }

    extract_content_by_ranges(pdf_file, topic_ranges)
