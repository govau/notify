import PyPDF2
from PyPDF2.utils import PdfReadError


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
