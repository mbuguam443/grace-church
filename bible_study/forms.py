from django import forms

from .models import BibleStudyComment, BibleStudyNote

VIDEO_EXTENSIONS = ['.mp4', '.webm', '.m4v', '.ogv']
AUDIO_EXTENSIONS = ['.mp3', '.m4a', '.wav', '.ogg', '.oga']
PDF_EXTENSIONS = ['.pdf']


class BibleStudyNoteForm(forms.ModelForm):
    class Meta:
        model = BibleStudyNote
        fields = [
            'title', 'bible_verse', 'study_date', 'teacher', 'series',
            'content', 'key_points', 'prayer_points', 'discussion_questions',
            'video', 'pdf_attachment', 'audio', 'video_url', 'is_active',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['video_url'].widget.attrs.update({
            'placeholder': 'https://youtube.com/watch?v=... or https://vimeo.com/...',
        })

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video and not any(video.name.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            raise forms.ValidationError('Only video files are allowed (%s).' % ', '.join(VIDEO_EXTENSIONS))
        return video

    def clean_pdf_attachment(self):
        pdf = self.cleaned_data.get('pdf_attachment')
        if pdf and not any(pdf.name.lower().endswith(ext) for ext in PDF_EXTENSIONS):
            raise forms.ValidationError('Only PDF files can be attached.')
        return pdf

    def clean_audio(self):
        audio = self.cleaned_data.get('audio')
        if audio and not any(audio.name.lower().endswith(ext) for ext in AUDIO_EXTENSIONS):
            raise forms.ValidationError('Only audio files are allowed (%s).' % ', '.join(AUDIO_EXTENSIONS))
        return audio


class BibleStudyCommentForm(forms.ModelForm):
    class Meta:
        model = BibleStudyComment
        fields = ['body', 'attachment']

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment and not attachment.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Only PDF files can be attached.')
        return attachment