import pytest
from docs.forms import DocumentForm

@pytest.mark.django_db
def test_document_form_valid():
    form = DocumentForm(data={"file_path": "/uploads/test.jpg"})
    assert form.is_valid()

@pytest.mark.django_db
def test_document_form_invalid():
    form = DocumentForm(data={})
    assert not form.is_valid()
