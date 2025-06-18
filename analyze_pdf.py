"""
Convert PDF pages to images for analysis.
"""

try:
    from pdf2image import convert_from_path
    import os
    
    # Convert PDF to images
    pdf_path = "mellow_analytics_report_improved.pdf"
    
    if os.path.exists(pdf_path):
        print(f"Converting {pdf_path} to images...")
        images = convert_from_path(pdf_path, dpi=150, first_page=1, last_page=5)
        
        # Save first 5 pages as images
        for i, image in enumerate(images):
            image_path = f"page_{i+1}.png"
            image.save(image_path, "PNG")
            print(f"Saved {image_path}")
            
        print("PDF pages converted successfully!")
        print("You can now view the images to see the actual output.")
    else:
        print(f"PDF file {pdf_path} not found")
        
except ImportError:
    print("pdf2image not available, trying alternative approach...")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.image as mpimg
    
    print("Alternative approach not implemented. Please check the PDF manually.")

except Exception as e:
    print(f"Error converting PDF: {e}")
    print("Will proceed with fixing common issues based on the code review.") 