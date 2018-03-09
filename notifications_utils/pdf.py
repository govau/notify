import PyPDF2
from PyPDF2 import PdfFileWriter
from PyPDF2.utils import PdfReadError
import io


def pdf_page_count(src_pdf):
    """
    Returns number of pages in a pdf file

    :param PyPDF2.PdfFileReader src_pdf: A File object or an object that supports the standard read and seek methods
    """
    try:
        pdf = PyPDF2.PdfFileReader(src_pdf)
    except AttributeError as e:
        raise PdfReadError("Could not open PDF file, stream is null", e)

    return pdf.numPages


def extract_page_from_pdf(src_pdf, page_number):
    """
    Retrieves a new PDF document with the page extracted from the source PDF file.

    :param src_pdf: File object or an object that supports the standard read and seek methods similar to a File object.
    :param page_number: The page number to retrieve (pages begin at zero)
    """
    pdf = PyPDF2.PdfFileReader(src_pdf)

    if pdf.numPages < page_number:
        raise PdfReadError("Page number requested: {} of {} does not exist in document".format(
            str(page_number),
            str(pdf.numPages)
        ))

    writer = PdfFileWriter()
    writer.addPage(pdf.getPage(page_number))

    pdf_bytes = io.BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    return pdf_bytes.read()
