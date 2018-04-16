import base64
from io import BytesIO

import PyPDF2
import pytest
from PyPDF2.utils import PdfReadError

from notifications_utils.pdf import pdf_page_count, extract_page_from_pdf
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


def test_extract_page_from_pdf_one_page_pdf():
    file_data = base64.b64decode(one_page_pdf)
    pdf_page = extract_page_from_pdf(BytesIO(file_data), 0)

    pdf_original = PyPDF2.PdfFileReader(BytesIO(file_data))

    pdf_new = PyPDF2.PdfFileReader(BytesIO(pdf_page))

    assert pdf_original.getPage(0).extractText() == pdf_new.getPage(0).extractText()


def test_extract_page_from_pdf_multi_page_pdf():
    file_data = base64.b64decode(multi_page_pdf)
    pdf_page = extract_page_from_pdf(BytesIO(file_data), 4)

    pdf_original = PyPDF2.PdfFileReader(BytesIO(file_data))

    pdf_new = PyPDF2.PdfFileReader(BytesIO(pdf_page))

    assert pdf_original.getPage(4).extractText() == pdf_new.getPage(0).extractText()
    assert pdf_original.getPage(3).extractText() != pdf_new.getPage(0).extractText()


def test_extract_page_from_pdf_request_page_out_of_bounds():
    with pytest.raises(PdfReadError) as e:
        file_data = base64.b64decode(one_page_pdf)
        extract_page_from_pdf(BytesIO(file_data), 4)

    assert 'Page number requested: 4 of 1 does not exist in document' in str(e.value)
