import re

from django.db import models

from accounts.models import User
from .about_defaults import about_defaults
from .modules import MODULES

_HEX_COLOR_RE = re.compile(r'^#([0-9a-fA-F]{6})$')
_DEFAULT_COLOR = '#A8704A'
_LIGHT_TEXT = '#ffffff'
_DARK_TEXT = '#1f2933'


def readable_text_color(background):
    """Return a foreground colour that stays readable on ``background``.

    White is the site's default text colour, so it is preferred unless the
    background is genuinely pale (a cream, pastel or near-white), where white
    would become invisible. 0.30 is the luminance where white text starts to
    fail, which keeps brand colours such as #4292c6 and #A8704A on white text.
    """
    match = _HEX_COLOR_RE.match((background or '').strip())
    if not match:
        return _LIGHT_TEXT
    digits = match.group(1)
    channels = [int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    luminance = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    return _DARK_TEXT if luminance > 0.30 else _LIGHT_TEXT


def color_rgb(hex_color):
    """Return ``R, G, B`` for a hex colour so it can be used inside ``rgba()``."""
    match = _HEX_COLOR_RE.match((hex_color or '').strip())
    if not match:
        return '255, 255, 255'
    digits = match.group(1)
    return ', '.join(str(int(digits[i:i + 2], 16)) for i in (0, 2, 4))


class RoleModulePermission(models.Model):
    role = models.CharField(max_length=20, choices=User.ROLE_CHOICES)
    module = models.CharField(max_length=50, choices=MODULES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('role', 'module')
        verbose_name_plural = 'Role module permissions'

    def __str__(self):
        return f"{self.get_role_display()} -> {self.get_module_display()}"

    @classmethod
    def allowed_modules_for(cls, role):
        perms = cls.objects.filter(role=role).values_list('module', flat=True)
        if not perms.exists():
            return None
        return set(perms)


class ChurchSetting(models.Model):
    church_name = models.CharField(max_length=200, default='Grace Church Munyaka')
    short_name = models.CharField(max_length=20, default='GC')
    logo = models.ImageField(upload_to='church/', blank=True, null=True)
    favicon = models.ImageField(upload_to='church/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='church/', blank=True, null=True, help_text='Homepage hero background (1920x1080 recommended)')
    events_image = models.ImageField(upload_to='church/', blank=True, null=True, help_text='Events section image')
    sermons_image = models.ImageField(upload_to='church/', blank=True, null=True, help_text='Sermons section image')
    cta_image = models.ImageField(upload_to='church/', blank=True, null=True, help_text='Call to action section image')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    currency = models.CharField(max_length=10, default='KES')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    primary_color = models.CharField(max_length=7, default='#A8704A')
    secondary_color = models.CharField(max_length=7, default='#4E3A2C')
    accent_color = models.CharField(max_length=7, default='#B5651D')
    gold_color = models.CharField(max_length=7, default='#C9A24B')
    navbar_color = models.CharField(
        max_length=7, blank=True,
        help_text='Solid navbar background colour. Leave blank to use the primary colour.',
    )
    footer_color = models.CharField(
        max_length=7, blank=True,
        help_text='Solid footer background colour. Leave blank to use the primary colour.',
    )
    section_color = models.CharField(
        max_length=7, blank=True,
        help_text='Solid background colour for section header bands. Leave blank to use the primary colour.',
    )
    audio_file = models.FileField(upload_to='church/audio/', blank=True, null=True, help_text='Homepage sermon player audio (MP3 recommended, keep under ~10MB)')
    audio_title = models.CharField(max_length=120, blank=True)
    audio_speaker = models.CharField(max_length=120, blank=True)
    service_times = models.TextField(blank=True, help_text='One per line')
    about_history_intro = models.TextField(
        null=True, blank=True,
        help_text='About page intro paragraph.',
    )
    about_history_body = models.TextField(
        null=True, blank=True,
        help_text='About page history. Separate paragraphs with a blank line.',
    )
    about_history_image = models.ImageField(
        upload_to='church/', null=True, blank=True,
        help_text='About page image (recommended 1280x575 or wider).',
    )
    about_call = models.TextField(
        null=True, blank=True,
        help_text='"Our Call" card text on the About page.',
    )
    about_divine_promise = models.TextField(
        null=True, blank=True,
        help_text='"Our Divine Promise" card text on the About page.',
    )
    about_milestones = models.TextField(
        null=True, blank=True,
        help_text='Key Milestones. One per line, format: Date | Description',
    )
    featured_event_title = models.CharField(
        max_length=200, null=True, blank=True,
        help_text='Featured event title on the Events page.',
    )
    featured_event_description = models.TextField(
        null=True, blank=True,
        help_text='Featured event description on the Events page.',
    )
    featured_event_image = models.ImageField(
        upload_to='church/', null=True, blank=True,
        help_text='Featured event image (leave blank for the default image).',
    )
    featured_event_date = models.CharField(
        max_length=100, null=True, blank=True,
        help_text='Featured event date, e.g. Nov 11-15, 2024.',
    )
    featured_event_time = models.CharField(
        max_length=100, null=True, blank=True,
        help_text='Featured event time, e.g. 6:00 PM - 9:00 PM.',
    )
    featured_event_venue = models.CharField(
        max_length=200, null=True, blank=True,
        help_text='Featured event venue.',
    )
    featured_event_audience = models.CharField(
        max_length=100, null=True, blank=True,
        help_text='Featured event audience, e.g. Everyone.',
    )
    featured_event_link = models.URLField(
        null=True, blank=True,
        help_text='Optional button link (leave blank to use the contact page).',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Church Setting'
        verbose_name_plural = 'Church Settings'

    def __str__(self):
        return self.church_name

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1, defaults=about_defaults())
        return obj

    @property
    def effective_navbar_color(self):
        return self.navbar_color or self.primary_color or _DEFAULT_COLOR

    @property
    def effective_footer_color(self):
        return self.footer_color or self.primary_color or _DEFAULT_COLOR

    @property
    def effective_section_color(self):
        return self.section_color or self.primary_color or _DEFAULT_COLOR

    @property
    def navbar_text_color(self):
        return readable_text_color(self.effective_navbar_color)

    @property
    def footer_text_color(self):
        return readable_text_color(self.effective_footer_color)

    @property
    def section_text_color(self):
        return readable_text_color(self.effective_section_color)

    @property
    def navbar_text_rgb(self):
        return color_rgb(self.navbar_text_color)

    @property
    def footer_text_rgb(self):
        return color_rgb(self.footer_text_color)

    @property
    def section_text_rgb(self):
        return color_rgb(self.section_text_color)

    @property
    def history_paragraphs(self):
        body = self.about_history_body or ''
        return [p.strip() for p in body.split('\n\n') if p.strip()]

    @property
    def call_paragraphs(self):
        return [p.strip() for p in (self.about_call or '').split('\n\n') if p.strip()]

    @property
    def divine_promise_paragraphs(self):
        return [p.strip() for p in (self.about_divine_promise or '').split('\n\n') if p.strip()]

    @property
    def milestones_list(self):
        items = []
        for raw in (self.about_milestones or '').splitlines():
            line = raw.strip()
            if not line:
                continue
            date_label, sep, description = line.partition('|')
            if sep:
                items.append({'date': date_label.strip(), 'description': description.strip()})
            else:
                items.append({'date': '', 'description': line})
        return items

    @property
    def audio_basename(self):
        if not self.audio_file:
            return ''
        return self.audio_file.name.rsplit('/', 1)[-1]


class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    kind = models.CharField(max_length=40, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user}"


class Leader(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=120, blank=True)
    photo = models.ImageField(upload_to='leaders/', blank=True, null=True)
    bio = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Leaders'

    def __str__(self):
        return self.name

    @property
    def initials(self):
        parts = [p for p in self.name.split() if p]
        if not parts:
            return '?'
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return parts[0][0].upper()
