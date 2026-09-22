from django.db.models.signals import post_save
from django.dispatch import receiver

from bible_study.models import BibleStudyNote
from communication.models import Announcement
from events.models import Event
from sermons.models import Sermon
from services.models import Service
from songs.models import Song

from .notify import broadcast


@receiver(post_save, sender=Announcement)
def on_announcement(sender, instance, created, **kwargs):
    if created and instance.is_active:
        broadcast(instance.title, instance.message, 'announcements')


@receiver(post_save, sender=Event)
def on_event(sender, instance, created, **kwargs):
    if created and instance.is_active:
        broadcast(instance.name, instance.description or 'A new church event is coming up.', 'events')


@receiver(post_save, sender=Sermon)
def on_sermon(sender, instance, created, **kwargs):
    if not created:
        return
    kind = 'devotions' if getattr(instance, 'category', '') == 'devotion' else 'sermons'
    broadcast(instance.title, instance.description or 'A new message is ready to read.', kind)


@receiver(post_save, sender=BibleStudyNote)
def on_bible_study(sender, instance, created, **kwargs):
    if created and instance.is_active:
        broadcast(instance.title, instance.bible_verse or 'New Bible study notes are ready.', 'bible-study')


@receiver(post_save, sender=Song)
def on_song(sender, instance, created, **kwargs):
    if created:
        broadcast(instance.title, 'New lyrics are in Songs & Hymns.', 'songs')


@receiver(post_save, sender=Service)
def on_service(sender, instance, created, **kwargs):
    if created:
        broadcast(instance.name, 'A service is on the calendar. Check in when you arrive.', 'attendance')
