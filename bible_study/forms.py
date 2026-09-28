from django import forms

from accounts.models import User
from ministries.models import Ministry
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
            'enable_registration', 'requires_approval', 'max_students',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['video_url'].widget.attrs.update({
            'placeholder': 'https://youtube.com/watch?v=... or https://vimeo.com/...',
        })
        self.fields['max_students'].widget.attrs.update({
            'placeholder': 'e.g. 10 (leave blank for unlimited)',
        })

    def clean_max_students(self):
        value = self.cleaned_data.get('max_students')
        if value is not None and value < 1:
            raise forms.ValidationError('Maximum students must be at least 1.')
        return value

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


class AddStudentForm(forms.Form):
    """Lets the teacher hand-pick members to place straight into the class."""

    student = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, is_staff=False, is_superuser=False),
        label='Select a member',
    )

    def __init__(self, *args, study=None, **kwargs):
        super().__init__(*args, **kwargs)
        if study is not None:
            self.fields['student'].queryset = User.objects.filter(
                is_active=True, is_staff=False, is_superuser=False,
            ).exclude(bible_study_enrollments__study=study)
        self.fields['student'].widget.attrs.update({'class': 'form-select'})


class AddStudentsForm(forms.Form):
    """Ministries-style multi-select so the teacher can pick several members
    at once for a targeted class (e.g. new comers or leaders)."""

    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True, is_staff=False, is_superuser=False),
        label='Select members',
        widget=forms.SelectMultiple(attrs={'size': '6', 'class': 'form-select'}),
    )

    def __init__(self, *args, study=None, **kwargs):
        super().__init__(*args, **kwargs)
        if study is not None:
            self.fields['students'].queryset = User.objects.filter(
                is_active=True, is_staff=False, is_superuser=False,
            ).exclude(bible_study_enrollments__study=study)


class TargetMinistryForm(forms.Form):
    """Teacher picks a ministry and all its members are added to the class."""

    ministry = forms.ModelChoiceField(
        queryset=Ministry.objects.filter(is_active=True),
        label='Select a ministry',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )