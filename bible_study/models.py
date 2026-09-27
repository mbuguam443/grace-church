from django.db import models


class BibleStudyNote(models.Model):
    title = models.CharField(max_length=300)
    bible_verse = models.CharField(max_length=200)
    study_date = models.DateField()
    teacher = models.CharField(max_length=200, blank=True)
    series = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    key_points = models.TextField(blank=True)
    prayer_points = models.TextField(blank=True)
    discussion_questions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-study_date']

    def __str__(self):
        return f"{self.title} - {self.bible_verse}"


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
