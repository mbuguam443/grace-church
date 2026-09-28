from django import forms

from accounts.models import User
from children.models import Child
from ministries.models import Ministry
from .models import CourseComment, SundaySchoolCourse

VIDEO_EXTENSIONS = ['.mp4', '.webm', '.m4v', '.ogv']
AUDIO_EXTENSIONS = ['.mp3', '.m4a', '.wav', '.ogg', '.oga']
PDF_EXTENSIONS = ['.pdf']


class SundaySchoolCourseForm(forms.ModelForm):
    # Optional: put children into the class in the same step as posting it.
    add_children = forms.ModelMultipleChoiceField(
        queryset=Child.objects.filter(is_active=True).select_related('parent'),
        required=False,
        label='Add these children now (optional)',
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'form-select'}),
        help_text='Hold Ctrl (or Cmd) to pick more than one. They are added straight away when you post.',
    )
    add_ministry = forms.ModelChoiceField(
        queryset=Ministry.objects.filter(is_active=True),
        required=False,
        label='Add all children of this ministry (optional)',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='The children of everyone in this ministry are added when you post.',
    )
    add_age_group = forms.ChoiceField(
        choices=[c for c in SundaySchoolCourse.AGE_GROUP_CHOICES if c[0] != 'all'],
        required=False,
        label='Add all children in this age group (optional)',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Every child whose age falls in this group is added when you post.',
    )

    class Meta:
        model = SundaySchoolCourse
        fields = [
            'title', 'age_group', 'lesson_date', 'scripture', 'memory_verse',
            'lesson', 'activities', 'video', 'pdf_attachment', 'audio', 'video_url', 'is_active',
            'enable_registration', 'requires_approval', 'max_students',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['video_url'].widget.attrs.update({
            'placeholder': 'https://youtube.com/watch?v=... or https://vimeo.com/...',
        })
        self.fields['max_students'].widget.attrs.update({
            'placeholder': 'e.g. 20 (leave blank for unlimited)',
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


class CourseCommentForm(forms.ModelForm):
    class Meta:
        model = CourseComment
        fields = ['body', 'attachment']

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment and not attachment.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Only PDF files can be attached.')
        return attachment


def active_children(exclude_course=None):
    """Children available to be put on a Sunday School class."""
    qs = Child.objects.filter(is_active=True).select_related('parent')
    if exclude_course is not None:
        qs = qs.exclude(course_enrollments__course=exclude_course)
    return qs


class AddChildForm(forms.Form):
    """Lets the teacher hand-pick a child to place straight into the class."""

    child = forms.ModelChoiceField(
        queryset=active_children(),
        label='Select a child',
    )

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['child'].queryset = active_children(exclude_course=course)
        self.fields['child'].widget.attrs.update({'class': 'form-select'})


class AddChildrenForm(forms.Form):
    """Ministries-style multi-select so the teacher can pick several children
    at once for a targeted class (e.g. a family or an age group)."""

    children = forms.ModelMultipleChoiceField(
        queryset=active_children(),
        label='Select children',
        widget=forms.SelectMultiple(attrs={'size': '8', 'class': 'form-select'}),
    )

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['children'].queryset = active_children(exclude_course=course)


class TargetMinistryForm(forms.Form):
    """Teacher picks a ministry and every child of its members is added."""

    ministry = forms.ModelChoiceField(
        queryset=Ministry.objects.filter(is_active=True),
        label='Select a ministry',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Adds the children of everyone in this ministry.',
    )


class TargetAgeGroupForm(forms.Form):
    """Teacher targets a whole age group of the Sunday School class."""

    age_group = forms.ChoiceField(
        choices=[c for c in SundaySchoolCourse.AGE_GROUP_CHOICES if c[0] != 'all'],
        label='Select an age group',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )