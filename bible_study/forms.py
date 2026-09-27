from django import forms

from .models import BibleStudyComment


class BibleStudyCommentForm(forms.ModelForm):
    class Meta:
        model = BibleStudyComment
        fields = ['body', 'attachment']

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment and not attachment.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Only PDF files can be attached.')
        return attachment