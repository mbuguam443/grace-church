import json

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from attendance.models import Attendance
from bible_study.models import BibleStudyNote
from core.models import Notification
from communication.models import Announcement
from events.models import Event, EventRegistration
from giving.models import Giving
from groups.models import Group
from members.models import Member
from prayer.models import PrayerRequest
from sermons.models import Sermon
from services.models import Service
from songs.models import Song

from .auth import get_member, token_required
from .models import ApiToken, DeviceToken

MAX_LIST = 100


def _photo_url(request, field):
    if field and hasattr(field, 'url'):
        return request.build_absolute_uri(field.url)
    return None


def _user_payload(request, user):
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
        'email': user.email,
        'phone': user.phone,
        'role': user.role,
        'role_label': user.get_role_display(),
        'photo_url': _photo_url(request, user.photo),
    }


def _member_payload(request, member):
    if member is None:
        return None
    return {
        'id': member.id,
        'member_number': member.member_number,
        'first_name': member.first_name,
        'middle_name': member.middle_name,
        'last_name': member.last_name,
        'full_name': member.first_name + (' ' + member.middle_name if member.middle_name else '') + ' ' + member.last_name,
        'gender': member.gender,
        'date_of_birth': member.date_of_birth.isoformat() if member.date_of_birth else None,
        'phone': member.phone,
        'email': member.email,
        'address': member.address,
        'photo_url': _photo_url(request, member.photo),
        'date_joined': member.date_joined.isoformat() if member.date_joined else None,
        'membership_status': member.membership_status,
        'membership_status_label': member.get_membership_status_display(),
        'membership_type': member.membership_type,
        'membership_type_label': member.get_membership_type_display(),
        'baptism_status': member.baptism_status,
        'baptism_date': member.baptism_date.isoformat() if member.baptism_date else None,
        'salvation_date': member.salvation_date.isoformat() if member.salvation_date else None,
        'marital_status': member.marital_status,
        'occupation': member.occupation,
        'emergency_contact_name': member.emergency_contact_name,
        'emergency_contact_phone': member.emergency_contact_phone,
        'family': member.family.name if member.family else None,
    }


def _giving_payload(g):
    return {
        'id': g.id,
        'amount': str(g.amount),
        'category': g.giving_category,
        'category_label': g.get_giving_category_display(),
        'date': g.date.isoformat(),
        'payment_method': g.payment_method,
        'payment_method_label': g.get_payment_method_display(),
        'reference_number': g.reference_number,
    }


def _attendance_payload(a):
    return {
        'id': a.id,
        'service': a.service.name,
        'date': a.service.date.isoformat(),
        'start_time': a.service.start_time.isoformat() if a.service.start_time else None,
        'location': a.service.location,
        'type': a.attendance_type,
        'recorded': a.created_at.isoformat(),
    }


def _service_payload(s, member_id=None):
    today = timezone.localdate()
    checked_in = bool(member_id and Attendance.objects.filter(service=s, member_id=member_id).exists())
    return {
        'id': s.id,
        'name': s.name,
        'date': s.date.isoformat(),
        'start_time': s.start_time.isoformat() if s.start_time else None,
        'end_time': s.end_time.isoformat() if s.end_time else None,
        'location': s.location,
        'preacher': s.preacher,
        'theme': s.theme,
        'bible_verse': s.bible_verse,
        'checked_in': checked_in,
        'can_check_in': s.date == today and not checked_in,
    }


def _group_payload(g, member_id=None):
    return {
        'id': g.id,
        'name': g.name,
        'description': g.description,
        'meeting_day': g.meeting_day,
        'meeting_time': g.meeting_time.strftime('%H:%M') if g.meeting_time else None,
        'location': g.location,
        'leader': g.leader.first_name + ' ' + g.leader.last_name if g.leader else None,
        'members_count': g.members.count(),
        'is_active': g.is_active,
    }


def _event_payload(request, e, member_id=None):
    registered = False
    if member_id and EventRegistration.objects.filter(event=e, member_id=member_id).exists():
        registered = True
    return {
        'id': e.id,
        'name': e.name,
        'description': e.description,
        'date': e.date.isoformat(),
        'time': e.time.isoformat() if e.time else None,
        'end_date': e.end_date.isoformat() if e.end_date else None,
        'location': e.location,
        'speaker': e.speaker,
        'capacity': e.capacity,
        'is_full': e.is_full,
        'registrations_count': e.registrations_count,
        'registration_required': e.registration_required,
        'registered': registered,
    }


def _announcement_payload(a):
    return {
        'id': a.id,
        'title': a.title,
        'message': a.message,
        'publish_date': a.publish_date.isoformat(),
        'expiry_date': a.expiry_date.isoformat() if a.expiry_date else None,
        'target_audience': a.target_audience,
    }


def _sermon_payload(request, s, detail=False):
    payload = {
        'id': s.id,
        'title': s.title,
        'speaker': s.speaker,
        'date': s.date.isoformat(),
        'bible_verse': s.bible_verse,
        'series': s.series,
        'category': s.category,
        'description': s.description,
        'youtube_url': s.youtube_url,
    }
    if detail:
        payload['sermon_notes'] = s.sermon_notes
        payload['pdf_url'] = _photo_url(request, s.pdf_file) if s.pdf_file else None
        payload['audio_url'] = _photo_url(request, s.audio_file) if s.audio_file else None
        payload['video_url'] = _photo_url(request, s.video_file) if s.video_file else None
    return payload


def _bible_note_payload(n, detail=False):
    payload = {
        'id': n.id,
        'title': n.title,
        'bible_verse': n.bible_verse,
        'study_date': n.study_date.isoformat(),
        'teacher': n.teacher,
        'series': n.series,
    }
    if detail:
        payload['content'] = n.content
        payload['key_points'] = n.key_points
        payload['prayer_points'] = n.prayer_points
        payload['discussion_questions'] = n.discussion_questions
    return payload


def _song_payload(song, detail=False):
    payload = {
        'id': song.id,
        'title': song.title,
        'category': song.category,
        'category_label': song.get_category_display(),
        'author': song.author,
        'scripture': song.scripture,
        'key': song.key,
        'tempo': song.tempo,
        'youtube_url': song.youtube_url,
    }
    if detail:
        payload['lyrics'] = song.lyrics
    return payload


def _notification_payload(n):
    return {
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'kind': n.kind,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat(),
    }


def _prayer_payload(p, member_id=None):
    return {
        'id': p.id,
        'title': p.title,
        'request': p.request,
        'category': p.category,
        'category_label': p.get_category_display(),
        'date': p.date.isoformat(),
        'status': p.status,
        'status_label': p.get_status_display(),
        'is_confidential': p.is_confidential,
        'is_mine': p.member_id == member_id,
    }


def _json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return {}


@csrf_exempt
@require_http_methods(['POST'])
def login_view(request):
    data = _json_body(request)
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    if not username or not password:
        return JsonResponse({'error': 'Username and password are required'}, status=400)
    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active:
        return JsonResponse({'error': 'Invalid username or password'}, status=401)
    token = ApiToken.create_for_user(user)
    member = get_member(user)
    return JsonResponse({
        'token': token.key,
        'user': _user_payload(request, user),
        'member': _member_payload(request, member),
    })


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def logout_view(request):
    request.api_token.delete()
    return JsonResponse({'ok': True})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def me_view(request):
    member = get_member(request.user)
    return JsonResponse({
        'user': _user_payload(request, request.user),
        'member': _member_payload(request, member),
    })


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def portal_view(request):
    user = request.user
    member = get_member(user)
    givings_total = None
    givings_count = 0
    attendance_count = 0
    if member:
        agg = Giving.objects.filter(member=member).aggregate(total=Sum('amount'))
        givings_total = str(agg['total']) if agg['total'] else '0'
        givings_count = Giving.objects.filter(member=member).count()
        attendance_count = Attendance.objects.filter(member=member).count()
    today = timezone.localdate()
    upcoming_events = Event.objects.filter(is_active=True, date__gte=today)[:5]
    announcements = Announcement.objects.filter(is_active=True)[:5]
    my_groups = member.groups.filter(is_active=True) if member else Group.objects.none()
    today_services = Service.objects.filter(date=today).order_by('start_time')
    member_id = getattr(member, 'id', None)
    return JsonResponse({
        'member': _member_payload(request, member),
        'unread_count': user.notifications.filter(is_read=False).count(),
        'counts': {
            'groups': my_groups.count(),
            'givings': givings_count,
            'givings_total': givings_total,
            'attendance': attendance_count,
            'events': Event.objects.filter(is_active=True, date__gte=today).count(),
            'announcements': Announcement.objects.filter(is_active=True).count(),
        },
        'groups': [_group_payload(g) for g in my_groups[:10]],
        'givings': [_giving_payload(g) for g in (member.givings.all()[:5] if member else [])],
        'attendance': [_attendance_payload(a) for a in (member.attendances.select_related('service').all()[:5] if member else [])],
        'events': [_event_payload(request, e, member_id) for e in upcoming_events],
        'announcements': [_announcement_payload(a) for a in announcements],
        'today_services': [_service_payload(s, member_id) for s in today_services],
    })


@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def profile_view(request):
    user = request.user
    member = get_member(user)
    if request.method == 'GET':
        return JsonResponse({
            'user': _user_payload(request, user),
            'member': _member_payload(request, member),
        })

    data = _json_body(request)
    fields = {
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email',
        'phone': 'phone',
    }
    for api_field, model_field in fields.items():
        if api_field in data and isinstance(data[api_field], str):
            setattr(user, model_field, data[api_field].strip())
    user.save()

    if member:
        member_fields = {
            'first_name': 'first_name',
            'middle_name': 'middle_name',
            'last_name': 'last_name',
            'phone': 'phone',
            'email': 'email',
            'address': 'address',
            'date_of_birth': 'date_of_birth',
            'occupation': 'occupation',
            'marital_status': 'marital_status',
            'emergency_contact_name': 'emergency_contact_name',
            'emergency_contact_phone': 'emergency_contact_phone',
        }
        changed = False
        for api_field, model_field in member_fields.items():
            if api_field in data:
                value = data[api_field]
                if isinstance(value, str):
                    value = value.strip()
                if api_field == 'date_of_birth':
                    value = value or None
                setattr(member, model_field, value)
                changed = True
        photo = request.FILES.get('photo')
        if photo:
            member.photo = photo
            changed = True
        if changed:
            member.save()

    return JsonResponse({'ok': True, 'user': _user_payload(request, user), 'member': _member_payload(request, member)})


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def change_password_view(request):
    data = _json_body(request)
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    if not request.user.check_password(old_password):
        return JsonResponse({'error': 'Current password is incorrect'}, status=400)
    if not new_password:
        return JsonResponse({'error': 'New password is required'}, status=400)
    try:
        validate_password(new_password, request.user)
    except ValidationError as exc:
        return JsonResponse({'error': '; '.join(exc.messages)}, status=400)
    request.user.set_password(new_password)
    request.user.save()
    return JsonResponse({'ok': True})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def groups_view(request):
    member = get_member(request.user)
    if member is None:
        return JsonResponse({'results': [], 'count': 0})
    qs = member.groups.filter(is_active=True).order_by('name')
    return JsonResponse({'results': [i for i in [_group_payload(g) for g in qs[:MAX_LIST]]], 'count': qs.count()})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def givings_view(request):
    member = get_member(request.user)
    qs = Giving.objects.filter(member=member) if member else Giving.objects.none()
    agg = qs.aggregate(total=Sum('amount'))
    return JsonResponse({
        'results': [_giving_payload(g) for g in qs[:MAX_LIST]],
        'count': qs.count(),
        'total': str(agg['total']) if agg['total'] else '0',
    })


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def attendance_view(request):
    member = get_member(request.user)
    qs = Attendance.objects.filter(member=member).select_related('service') if member else Attendance.objects.none()
    return JsonResponse({
        'results': [_attendance_payload(a) for a in qs[:MAX_LIST]],
        'count': qs.count(),
    })


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def services_view(request):
    member = get_member(request.user)
    today = timezone.localdate()
    qs = Service.objects.filter(date__gte=today).order_by('date', 'start_time')[:MAX_LIST]
    member_id = getattr(member, 'id', None)
    return JsonResponse({
        'results': [_service_payload(s, member_id) for s in qs],
        'count': qs.count(),
    })


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def service_attend_view(request, service_id):
    member = get_member(request.user)
    if member is None:
        return JsonResponse({'error': 'No member profile linked to this account'}, status=400)
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)
    today = timezone.localdate()
    if service.date > today:
        return JsonResponse({'error': 'This service is not open for check-in yet'}, status=400)
    if service.date < today:
        return JsonResponse({'error': 'Check-in for this service has closed'}, status=400)
    Attendance.objects.get_or_create(
        service=service,
        member=member,
        defaults={'attendance_type': 'member'},
    )
    return JsonResponse({'ok': True, 'checked_in': True, 'service': _service_payload(service, member.id)})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def events_view(request):
    member = get_member(request.user)
    qs = Event.objects.filter(is_active=True, date__gte=timezone.localdate()).order_by('date')[:MAX_LIST]
    return JsonResponse({
        'results': [_event_payload(request, e, getattr(member, 'id', None)) for e in qs],
        'count': qs.count(),
    })


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def event_register_view(request, event_id):
    member = get_member(request.user)
    if member is None:
        return JsonResponse({'error': 'No member profile linked to this account'}, status=400)
    try:
        event = Event.objects.get(pk=event_id, is_active=True)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    registration, created = EventRegistration.objects.get_or_create(event=event, member=member)
    if not created:
        registration.delete()
    return JsonResponse({'ok': True, 'registered': created, 'event': _event_payload(request, event, member.id)})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def announcements_view(request):
    qs = Announcement.objects.filter(is_active=True)[:MAX_LIST]
    return JsonResponse({'results': [_announcement_payload(a) for a in qs], 'count': qs.count()})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def sermons_view(request):
    qs = Sermon.objects.all()[:MAX_LIST]
    return JsonResponse({'results': [_sermon_payload(request, s) for s in qs], 'count': qs.count()})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def sermon_detail_view(request, sermon_id):
    try:
        s = Sermon.objects.get(pk=sermon_id)
    except Sermon.DoesNotExist:
        return JsonResponse({'error': 'Sermon not found'}, status=404)
    return JsonResponse(_sermon_payload(request, s, detail=True))


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def devotions_view(request):
    qs = Sermon.objects.filter(category='devotion')[:MAX_LIST]
    return JsonResponse({'results': [_sermon_payload(request, s) for s in qs], 'count': qs.count()})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def bible_study_view(request):
    qs = BibleStudyNote.objects.filter(is_active=True)[:MAX_LIST]
    return JsonResponse({'results': [_bible_note_payload(n) for n in qs], 'count': qs.count()})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def bible_study_detail_view(request, note_id):
    try:
        n = BibleStudyNote.objects.get(pk=note_id, is_active=True)
    except BibleStudyNote.DoesNotExist:
        return JsonResponse({'error': 'Study note not found'}, status=404)
    return JsonResponse(_bible_note_payload(n, detail=True))


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def songs_view(request):
    qs = Song.objects.all()[:MAX_LIST]
    return JsonResponse({'results': [_song_payload(s) for s in qs], 'count': qs.count()})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def song_detail_view(request, song_id):
    try:
        song = Song.objects.get(pk=song_id)
    except Song.DoesNotExist:
        return JsonResponse({'error': 'Song not found'}, status=404)
    return JsonResponse(_song_payload(song, detail=True))


@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def notifications_view(request):
    if request.method == 'GET':
        qs = request.user.notifications.all()[:MAX_LIST]
        return JsonResponse({
            'results': [_notification_payload(n) for n in qs],
            'count': qs.count(),
            'unread_count': request.user.notifications.filter(is_read=False).count(),
        })

    data = _json_body(request)
    requested_ids = data.get('ids') or []
    ids = [int(i) for i in requested_ids if isinstance(i, int) or str(i).isdigit()]
    if ids:
        request.user.notifications.filter(id__in=ids).update(is_read=True)
    else:
        request.user.notifications.update(is_read=True)
    return JsonResponse({
        'ok': True,
        'unread_count': request.user.notifications.filter(is_read=False).count(),
    })


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def device_token_view(request):
    data = _json_body(request)
    token = (data.get('token') or '').strip()
    if not token:
        return JsonResponse({'error': 'Device token is required'}, status=400)
    device, created = DeviceToken.objects.update_or_create(
        token=token,
        defaults={'user': request.user, 'platform': data.get('platform') or ''},
    )
    return JsonResponse({'ok': True, 'created': created})


@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def prayers_view(request):
    member = get_member(request.user)
    if request.method == 'GET':
        qs = PrayerRequest.objects.filter(member=member) if member else PrayerRequest.objects.none()
        return JsonResponse({
            'results': [_prayer_payload(p, getattr(member, 'id', None)) for p in qs[:MAX_LIST]],
            'count': qs.count(),
        })
    data = _json_body(request)
    title = (data.get('title') or '').strip()
    body = (data.get('request') or '').strip()
    if not title or not body:
        return JsonResponse({'error': 'Title and request are required'}, status=400)
    prayer = PrayerRequest.objects.create(
        member=member,
        title=title[:200],
        request=body,
        category=data.get('category') or 'other',
        is_confidential=bool(data.get('is_confidential', False)),
    )
    return JsonResponse({'ok': True, 'prayer': _prayer_payload(prayer, getattr(member, 'id', None))}, status=201)