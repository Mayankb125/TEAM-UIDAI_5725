import os
import markdown
from xhtml2pdf import pisa

# Configuration
INPUT_FILE = r"C:\Users\mayan\.gemini\antigravity\brain\685ebe2a-d1f5-4fce-9f36-275947cbcb4c\final_report.md"
OUTPUT_PDF = r"d:\UIDAI data hackathon\outputs\UIDAI_Hackathon_Final_Report_Team_Antigravity.pdf"

# Custom CSS for the PDF
CSS = """
<style>
    body {
        font-family: Helvetica, Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #333;
        margin: 20px;
    }
    h1 {
        font-size: 24pt;
        color: #1a237e;
        border-bottom: 2px solid #1a237e;
        padding-bottom: 10px;
        margin-top: 30px;
    }
    h2 {
        font-size: 18pt;
        color: #283593;
        margin-top: 25px;
        border-bottom: 1px solid #ddd;
    }
    h3 {
        font-size: 14pt;
        color: #3f51b5;
        margin-top: 20px;
    }
    p {
        margin-bottom: 15px;
        text-align: justify;
    }
    li {
        margin-bottom: 8px;
    }
    img {
        max-width: 100%;
        height: auto;
        margin: 20px 0;
        border: 1px solid #eee;
        padding: 5px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f5f5f5;
        color: #333;
    }
    blockquote {
        background-color: #f9f9f9;
        border-left: 5px solid #3f51b5;
        padding: 10px;
        margin: 20px 0;
    }
    .cover-title {
        text-align: center;
        margin-top: 200px;
        font-size: 32pt;
        font-weight: bold;
        color: #1a237e;
    }
    .cover-subtitle {
        text-align: center;
        font-size: 16pt;
        color: #666;
        margin-bottom: 100px;
    }
</style>
"""

def convert_md_to_pdf():
    print("Reading Markdown file...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert Markdown to HTML
    print("Converting to HTML...")
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
    
    # Wrap in HTML structure
    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        {CSS}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Generate PDF
    print(f"Generating PDF: {OUTPUT_PDF}")
    with open(OUTPUT_PDF, "wb") as output_file:
        pisa_status = pisa.CreatePDF(
            full_html,
            dest=output_file
        )

    if pisa_status.err:
        print("❌ Error generating PDF")
    else:
        print("✅ PDF generated successfully!")

if __name__ == "__main__":
    convert_md_to_pdf()
