import fitz  # PyMuPDF
import re
import logging
import os
import traceback

logger = logging.getLogger(__name__)

def process_pdf(input_path, output_path):
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            raise Exception(f"Input file not found: {input_path}")
            
        logger.info(f"Opening PDF: {input_path}")
        # Open the PDF
        doc = fitz.open(input_path)
        
        if doc.page_count == 0:
            raise Exception("PDF has no pages")
            
        logger.info(f"PDF has {doc.page_count} pages")
        
        # Process each page
        for page_num in range(doc.page_count):
            try:
                page = doc[page_num]
                logger.info(f"Processing page {page_num + 1}")
                
                # Extract text
                text = page.get_text()
                
                # Find all instances of numbers containing "100"
                pattern = r'\b\d*100\d*\b'  # Matches numbers containing 100
                matches = list(re.finditer(pattern, text))
                
                logger.info(f"Found {len(matches)} matches on page {page_num + 1}")
                
                # Add highlight for each instance
                for match in matches:
                    try:
                        match_text = match.group()
                        logger.info(f"Highlighting '{match_text}'")
                        
                        # Find the text instance on the page
                        instances = page.search_for(match_text)
                        
                        if not instances:
                            logger.warning(f"Could not find '{match_text}' on page {page_num + 1}")
                            continue
                            
                        # Add red highlight for each instance
                        for inst in instances:
                            highlight = page.add_highlight_annot(inst)
                            highlight.set_colors(stroke=(1, 0, 0))  # RGB for red
                            highlight.update()
                            
                    except Exception as e:
                        logger.error(f"Error highlighting match '{match_text}': {str(e)}")
                        logger.error(traceback.format_exc())
                        
            except Exception as e:
                logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Save the processed PDF
        logger.info(f"Saving processed PDF to {output_path}")
        doc.save(output_path)
        doc.close()
        
        # Verify the output file was created
        if not os.path.exists(output_path):
            raise Exception("Failed to save output file")
            
        logger.info("PDF processing completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to process PDF: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Failed to process PDF: {str(e)}") 