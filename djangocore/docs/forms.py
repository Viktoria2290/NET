from django import forms

class UploadFileForm(forms.Form):
    """Форма для загрузки файла пользователем.

    Attributes:
        file (FileField): Поле для выбора файла для загрузки.
    """
    file = forms.FileField()

class DeleteDocForm(forms.Form):
    """Форма для удаления документов по их ID.

    Attributes:
        doc_ids (CharField): Поле для ввода ID документов, разделенных запятыми.
    """
    doc_ids = forms.CharField(max_length=100, help_text='Введите ID документов через запятую')

class AnalyseDocForm(forms.Form):
    """Форма для анализа документа по его ID.

    Attributes:
        doc_id (IntegerField): Поле для ввода ID документа для анализа.
    """
    doc_id = forms.IntegerField()

class GetTextForm(forms.Form):
    """Форма для получения текста из документа по его ID.

    Attributes:
        doc_id (IntegerField): Поле для ввода ID документа для извлечения текста.
    """
    doc_id = forms.IntegerField()
