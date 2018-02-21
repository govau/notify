import base64
from io import BytesIO

import pytest
from PyPDF2.utils import PdfReadError

from notifications_utils.pdf import pdf_page_count
from tests.pdf_consts import one_page_pdf, multi_page_pdf, not_pdf


def test_pdf_page_count_src_pdf_is_null():
    with pytest.raises(PdfReadError):
        pdf_page_count(None)


def test_pdf_page_count_src_pdf_has_one_page():
    file_data = base64.b64decode(one_page_pdf)
    num = pdf_page_count(BytesIO(file_data))
    assert num == 1


def test_pdf_page_count_src_pdf_has_multiple_pages():
    file_data = base64.b64decode(multi_page_pdf)
    num = pdf_page_count(BytesIO(file_data))
    assert num == 10


def test_pdf_page_count_src_pdf_not_a_pdf():
    with pytest.raises(PdfReadError):
        file_data = base64.b64decode(not_pdf)
        pdf_page_count(BytesIO(file_data))
