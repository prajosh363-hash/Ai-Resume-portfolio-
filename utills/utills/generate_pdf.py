import pdfkit
import os
from typing import Optional
import tempfile

def render_pdf(html_content: str, output_path: str = "resume.pdf") -> str:
    """
    Convert HTML resume to PDF format
    
    Args:
        html_content: HTML string of the resume
        output_path: Path to save the PDF file
        
    Returns:
        Path to the generated PDF file
    """
    # Configure pdfkit options
    options = {
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        'quiet': ''
    }
    
    # Add CSS for better PDF styling
    css = '''
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .resume-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #2c3e50;
        }
        
        .name {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .contact-info {
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        
        .section {
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }
        
        .job-title {
            font-weight: bold;
            color: #34495e;
        }
        
        .company {
            color: #7f8c8d;
            font-style: italic;
        }
        
        .date {
            float: right;
            color: #95a5a6;
        }
        
        .bullet-points {
            margin-left: 20px;
            margin-top: 5px;
        }
        
        .bullet-points li {
            margin-bottom: 3px;
        }
        
        .skills-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .skill-tag {
            background-color: #ecf0f1;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            color: #2c3e50;
        }
        
        @media print {
            body {
                font-size: 12pt;
            }
            
            .no-print {
                display: none;
            }
        }
    </style>
    '''
    
    # Wrap HTML content with proper structure
    full_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resume</title>
        {css}
    </head>
    <body>
        <div class="resume-container">
            {html_content}
        </div>
    </body>
    </html>
    '''
    
    try:
        # Try to find wkhtmltopdf in common locations
        config = None
        wkhtmltopdf_paths = [
            '/usr/local/bin/wkhtmltopdf',
            '/usr/bin/wkhtmltopdf',
            'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe',
            os.path.join(os.path.dirname(__file__), 'wkhtmltopdf')
        ]
        
        for path in wkhtmltopdf_paths:
            if os.path.exists(path):
                config = pdfkit.configuration(wkhtmltopdf=path)
                break
        
        # Generate PDF
        pdfkit.from_string(full_html, output_path, options=options, configuration=config)
        
        # Check if file was created
        if os.path.exists(output_path):
            return output_path
        else:
            raise Exception("PDF file was not created")
            
    except Exception as e:
        # Fallback: Create a simple text-based PDF
        print(f"PDF generation error: {str(e)}. Using fallback method.")
        return _create_fallback_pdf(html_content, output_path)

def _create_fallback_pdf(html_content: str, output_path: str) -> str:
    """Create a simple PDF as fallback"""
    from fpdf import FPDF
    
    # Extract text from HTML
    import re
    text = re.sub(r'<[^>]+>', '', html_content)
    text = re.sub(r'\s+', ' ', text)
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Add text (split into chunks to avoid encoding issues)
    lines = text.split('\n')
    for line in lines[:50]:  # Limit to first 50 lines
        if line.strip():
            try:
                pdf.multi_cell(0, 10, line[:200])  # Limit line length
            except:
                pass
    
    pdf.output(output_path)
    return output_path
