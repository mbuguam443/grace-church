import re
from urllib.parse import quote

from django.conf import settings
from django.db import models


class BibleStudyNote(models.Model):
    title = models.CharField(max_length=300)
    bible_verse = models.CharField(max_length=200)
    study_date = models.DateField()
    teacher = models.ForeignKey(
        'members.Member', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bible_studies_taught',
        help_text='Teacher, chosen from the member list.',
    )
    series = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    key_points = models.TextField(blank=True)
    prayer_points = models.TextField(blank=True)
    discussion_questions = models.TextField(blank=True)
    video = models.FileField(
        upload_to='bible_study/', blank=True, null=True,
        help_text='Video file (e.g. MP4, WebM) shared with this study.',
    )
    pdf_attachment = models.FileField(
        upload_to='bible_study/', blank=True, null=True,
        help_text='PDF document shared with this study.',
    )
    audio = models.FileField(
        upload_to='bible_study/', blank=True, null=True,
        help_text='Audio file (e.g. MP3, M4A, OGG) shared with this study.',
    )
    video_url = models.URLField(
        blank=True,
        help_text='External video link (YouTube, Vimeo, Facebook, Dailymotion, etc.). Plays inline on the site.',
    )
    is_active = models.BooleanField(default=True)
    enable_registration = models.BooleanField(
        default=False,
        help_text='Show a "Join the Class" button and let members enrol.',
    )
    max_students = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Maximum number of students. Leave blank for unlimited.',
    )
    requires_approval = models.BooleanField(
        default=False,
        help_text='If checked, the teacher must approve each join request.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-study_date']

    def __str__(self):
        return f"{self.title} - {self.bible_verse}"

    @property
    def teacher_name(self):
        if not self.teacher:
            return ''
        return ('%s %s' % (self.teacher.first_name, self.teacher.last_name)).strip()

    @property
    def video_id(self):
        match = re.search(
            r'(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/|live\/)|youtu\.be\/)([\w-]{6,})',
            self.video_url or '',
        )
        return match.group(1) if match else ''

    @property
    def video_embed_url(self):
        """Embeddable player URL so the video plays inline on the site."""
        url = (self.video_url or '').strip()
        if not url:
            return ''
        if self.video_id:
            return 'https://www.youtube-nocookie.com/embed/%s?rel=0' % self.video_id
        match = re.search(r'(?:vimeo\.com\/)(?:video\/)?(\d+)', url)
        if match:
            return 'https://player.vimeo.com/video/%s' % match.group(1)
        match = re.search(r'(?:dailymotion\.com\/video\/)([a-zA-Z0-9]+)', url)
        if match:
            return 'https://www.dailymotion.com/embed/video/%s' % match.group(1)
        if 'facebook.com' in url:
            return 'https://www.facebook.com/plugins/video.php?href=%s&show_text=false&width=560' % quote(url, safe=':/?&=')
        return url

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='approved').count()

    @property
    def pending_count(self):
        return self.enrollments.filter(status='pending').count()

    @property
    def is_full(self):
        return bool(self.max_students and self.enrolled_count >= self.max_students)

    @property
    def spots_left(self):
        if not self.max_students:
            return None
        return max(0, self.max_students - self.enrolled_count)


class BibleStudyEnrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    study = models.ForeignKey(BibleStudyNote, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bible_study_enrollments',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['joined_at']
        unique_together = ('study', 'student')

    def __str__(self):
        return "%s -> %s (%s)" % (self.student_name, self.study.title, self.get_status_display())

    @property
    def student_name(self):
        return self.student.get_full_name() or self.student.username


class BibleStudyComment(models.Model):
    study = models.ForeignKey(BibleStudyNote, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='bible_study_comments')
    body = models.TextField()
    attachment = models.FileField(
        upload_to='bible_study/', blank=True, null=True,
        help_text='Optional PDF attachment. Only visible to administrators.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.name} on {self.study.title}"

    @property
    def name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def attachment_is_pdf(self):
        if not self.attachment:
            return False
        return self.attachment.name.lower().endswith('.pdf')
