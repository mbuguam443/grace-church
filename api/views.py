import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from attendance.models import Attendance
from bible_study.models import BibleStudyEnrollment, BibleStudyNote
from children.models import Child, ChildAttendance
from core.models import Notification
from communication.models import Announcement
from events.models import Event, EventRegistration
from facilities.models import Facility, FacilityBooking
from giving.models import Giving, OnlineGiving
from groups.models import Group
from members.models import Member
from ministries.models import Ministry
from prayer.models import PrayerRequest
from sermons.models import Sermon
from services.models import Service
from songs.models import Song
from sunday_school.models import CourseComment, CourseEnrollment, SundaySchoolCourse

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
        'end_time': e.end_time.isoformat() if e.end_time else None,
        'time_range': e.time_range,
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
        'has_audio': bool(s.audio_file),
        'has_video': bool(s.video_file),
        'has_pdf': bool(s.pdf_file),
    }
    if detail:
        payload['sermon_notes'] = s.sermon_notes
        payload['pdf_url'] = _photo_url(request, s.pdf_file) if s.pdf_file else None
        payload['audio_url'] = _photo_url(request, s.audio_file) if s.audio_file else None
        payload['video_url'] = _photo_url(request, s.video_file) if s.video_file else None
    return payload


def _bible_note_payload(n, detail=False, user=None):
    payload = {
        'id': n.id,
        'title': n.title,
        'bible_verse': n.bible_verse,
        'study_date': n.study_date.isoformat(),
        'teacher': n.teacher,
        'series': n.series,
        'enrolled_count': n.enrolled_count,
        'is_full': n.is_full,
        'spots_left': n.spots_left,
        'enable_registration': n.enable_registration,
        'requires_approval': n.requires_approval,
        'my_enrollment': None,
    }
    if user is not None:
        enrollment = n.enrollments.filter(student=user).first()
        if enrollment is not None:
            payload['my_enrollment'] = {
                'id': enrollment.id,
                'status': enrollment.status,
                'status_label': enrollment.get_status_display(),
                'joined_at': enrollment.joined_at.isoformat(),
            }
        if not detail:
            payload['can_join'] = bool(
                n.enable_registration
                and not n.is_full
                and not user.can_manage_content
                and payload['my_enrollment'] is None
            )
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
    return JsonResponse({
        'results': [_bible_note_payload(n, user=request.user) for n in qs],
        'count': qs.count(),
    })


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def bible_study_detail_view(request, note_id):
    try:
        n = BibleStudyNote.objects.get(pk=note_id, is_active=True)
    except BibleStudyNote.DoesNotExist:
        return JsonResponse({'error': 'Study note not found'}, status=404)
    return JsonResponse(_bible_note_payload(n, detail=True, user=request.user))


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
# ---------------------------------------------------------------------------
# Sunday School
# ---------------------------------------------------------------------------

def _my_child_ids(user):
    member = get_member(user)
    if member is None:
        return []
    return list(member.children.values_list('pk', flat=True))


def _enrollment_payload(enrollment):
    if enrollment is None:
        return None
    return {
        'id': enrollment.id,
        'status': enrollment.status,
        'status_label': enrollment.get_status_display(),
        'is_child': enrollment.is_child,
        'student_name': enrollment.student_name,
        'parent_name': enrollment.parent_name,
        'joined_at': enrollment.joined_at.isoformat(),
    }


def _course_payload(request, course, user, child_ids, detail=False):
    enrollment = None
    if child_ids:
        from django.db.models import Q
        enrollment = course.enrollments.filter(
            Q(student=user) | Q(child_id__in=child_ids)
        ).first()
    else:
        enrollment = course.enrollments.filter(student=user).first()
    can_view = (
        user.can_manage_content
        or not course.enable_registration
        or (enrollment is not None and enrollment.status == 'approved')
    )
    payload = {
        'id': course.id,
        'title': course.title,
        'age_group': course.age_group,
        'age_group_label': course.get_age_group_display(),
        'lesson_date': course.lesson_date.isoformat() if course.lesson_date else None,
        'scripture': course.scripture,
        'video_url': course.video_url,
        'enrolled_count': course.enrolled_count,
        'pending_count': course.pending_count,
        'max_students': course.max_students,
        'spots_left': course.spots_left,
        'is_full': course.is_full,
        'enable_registration': course.enable_registration,
        'requires_approval': course.requires_approval,
        'can_join': bool(course.enable_registration and not course.is_full
                         and not user.can_manage_content and enrollment is None),
        'can_view_content': can_view,
        'my_enrollment': _enrollment_payload(enrollment),
    }
    if detail:
        payload.update({
            'memory_verse': course.memory_verse if can_view else '',
            'lesson': course.lesson if can_view else '',
            'activities': course.activities if can_view else '',
            'updated_at': course.updated_at.isoformat(),
            # A parent with several children on the class needs to know which.
            'my_children_on_course': [
                e.student_name for e in course.enrollments.filter(child_id__in=child_ids)
                if e.child_id
            ] if child_ids else [],
        })
        # Files are only handed out to someone allowed to read the lesson.
        if can_view:
            payload['pdf_url'] = _photo_url(request, course.pdf_attachment)
            payload['audio_url'] = _photo_url(request, course.audio)
            payload['video_file_url'] = _photo_url(request, course.video)
        else:
            payload['pdf_url'] = None
            payload['audio_url'] = None
            payload['video_file_url'] = None
    return payload


def _course_comment_payload(request, comment, user):
    payload = {
        'id': comment.id,
        'body': comment.body,
        'author': comment.name,
        'created_at': comment.created_at.isoformat(),
        'is_mine': comment.user_id == user.id,
        'can_delete': comment.user_id == user.id or user.is_admin_user,
    }
    # Attachments are staff-only, same as on the website.
    payload['attachment_url'] = _photo_url(request, comment.attachment) if user.is_admin_user else None
    return payload


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def sunday_school_list_view(request):
    child_ids = _my_child_ids(request.user)
    qs = SundaySchoolCourse.objects.filter(is_active=True)
    age_group = (request.GET.get('age_group') or '').strip()
    if age_group:
        qs = qs.filter(age_group=age_group)
    search = (request.GET.get('search') or '').strip()
    if search:
        from django.db.models import Q
        qs = qs.filter(Q(title__icontains=search) | Q(scripture__icontains=search)
                       | Q(lesson__icontains=search))
    qs = qs.prefetch_related('enrollments__child__parent', 'enrollments__student')
    results = [_course_payload(request, c, request.user, child_ids) for c in qs[:MAX_LIST]]
    return JsonResponse({'results': results, 'count': qs.count()})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def sunday_school_detail_view(request, course_id):
    course = get_object_or_404(SundaySchoolCourse, pk=course_id, is_active=True)
    child_ids = _my_child_ids(request.user)
    payload = _course_payload(request, course, request.user, child_ids, detail=True)
    comments = course.comments.select_related('user')
    return JsonResponse({
        'course': payload,
        'comments': [_course_comment_payload(request, cm, request.user) for cm in comments[:MAX_LIST]],
    })


@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def sunday_school_join_view(request, course_id):
    course = get_object_or_404(SundaySchoolCourse, pk=course_id, is_active=True)
    if not course.enable_registration:
        return JsonResponse({'error': 'Registration is not open for this class'}, status=400)
    if request.user.can_manage_content:
        return JsonResponse({'error': 'Teachers cannot join their own class'}, status=400)
    if course.is_full:
        return JsonResponse({'error': 'This class is already full'}, status=400)
    if course.enrollments.filter(student=request.user).exists():
        return JsonResponse({'error': 'You have already joined this class'}, status=400)
    enrollment = CourseEnrollment.objects.create(
        course=course,
        student=request.user,
        status='pending' if course.requires_approval else 'approved',
    )
    message = 'Join request sent, waiting for teacher approval.' if course.requires_approval \
        else 'You have joined this class.'
    return JsonResponse({
        'ok': True,
        'message': message,
        'enrollment': _enrollment_payload(enrollment),
    }, status=201)


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def sunday_school_leave_view(request, course_id):
    course = get_object_or_404(SundaySchoolCourse, pk=course_id)
    enrollment = course.enrollments.filter(student=request.user).first()
    if enrollment is None:
        return JsonResponse({'error': 'You are not on this class'}, status=400)
    enrollment.delete()
    return JsonResponse({'ok': True, 'message': 'You have left this class.'})


@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def sunday_school_comment_view(request, course_id):
    course = get_object_or_404(SundaySchoolCourse, pk=course_id, is_active=True)
    if request.method == 'GET':
        comments = course.comments.select_related('user')
        return JsonResponse({
            'results': [_course_comment_payload(request, cm, request.user) for cm in comments[:MAX_LIST]],
            'count': comments.count(),
        })
    data = _json_body(request)
    body = (data.get('body') or '').strip()
    if not body:
        return JsonResponse({'error': 'Please write something first'}, status=400)
    comment = course.comments.create(user=request.user, body=body)
    return JsonResponse({'ok': True, 'comment': _course_comment_payload(request, comment, request.user)},
                        status=201)


@csrf_exempt
@token_required
@require_http_methods(['POST', 'DELETE'])
def sunday_school_comment_delete_view(request, course_id, comment_id):
    course = get_object_or_404(SundaySchoolCourse, pk=course_id)
    comment = get_object_or_404(CourseComment, pk=comment_id, course=course)
    if comment.user_id != request.user.id and not request.user.is_admin_user:
        return JsonResponse({'error': 'You can only delete your own comment'}, status=403)
    comment.delete()
    return JsonResponse({'ok': True})


# ---------------------------------------------------------------------------
# Bible study enrolment and discussion
# ---------------------------------------------------------------------------

@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def bible_study_join_view(request, note_id):
    note = get_object_or_404(BibleStudyNote, pk=note_id, is_active=True)
    if not note.enable_registration:
        return JsonResponse({'error': 'Registration is not open for this study'}, status=400)
    if request.user.can_manage_content:
        return JsonResponse({'error': 'Teachers cannot join their own study'}, status=400)
    if note.is_full:
        return JsonResponse({'error': 'This study is already full'}, status=400)
    if note.enrollments.filter(student=request.user).exists():
        return JsonResponse({'error': 'You have already joined this study'}, status=400)
    enrollment = BibleStudyEnrollment.objects.create(
        study=note,
        student=request.user,
        status='pending' if note.requires_approval else 'approved',
    )
    message = 'Join request sent, waiting for teacher approval.' if note.requires_approval \
        else 'You have joined this study.'
    return JsonResponse({'ok': True, 'message': message, 'id': enrollment.id}, status=201)


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def bible_study_leave_view(request, note_id):
    note = get_object_or_404(BibleStudyNote, pk=note_id)
    enrollment = note.enrollments.filter(student=request.user).first()
    if enrollment is None:
        return JsonResponse({'error': 'You are not on this study'}, status=400)
    enrollment.delete()
    return JsonResponse({'ok': True, 'message': 'You have left this study.'})


@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def bible_study_comment_view(request, note_id):
    note = get_object_or_404(BibleStudyNote, pk=note_id, is_active=True)
    if request.method == 'GET':
        comments = note.comments.select_related('user')
        return JsonResponse({
            'results': [
                {
                    'id': cm.id,
                    'body': cm.body,
                    'author': cm.name,
                    'created_at': cm.created_at.isoformat(),
                    'is_mine': cm.user_id == request.user.id,
                    'can_delete': cm.user_id == request.user.id or request.user.is_admin_user,
                }
                for cm in comments[:MAX_LIST]
            ],
            'count': comments.count(),
        })
    data = _json_body(request)
    body = (data.get('body') or '').strip()
    if not body:
        return JsonResponse({'error': 'Please write something first'}, status=400)
    comment = note.comments.create(user=request.user, body=body)
    return JsonResponse({'ok': True, 'comment': {'id': comment.id, 'body': comment.body}}, status=201)

# ---------------------------------------------------------------------------
# Children
# ---------------------------------------------------------------------------

def _child_payload(request, child):
    today = timezone.localdate()
    attendance = child.attendances.filter(date=today).first()
    courses = child.course_enrollments.filter(course__is_active=True).select_related('course')
    return {
        'id': child.id,
        'first_name': child.first_name,
        'last_name': child.last_name,
        'full_name': child.get_full_name(),
        'date_of_birth': child.date_of_birth.isoformat(),
        'age': child.age,
        'age_group': child.age_group,
        'age_group_label': child.age_group_display,
        'gender': child.gender,
        'school_class': child.school_class,
        'teacher': child.teacher,
        'allergies': child.allergies,
        'emergency_contact': child.emergency_contact,
        'photo_url': _photo_url(request, child.photo),
        'is_active': child.is_active,
        'checked_in_today': bool(attendance and attendance.checked_in),
        'checked_out_today': bool(attendance and attendance.checked_out),
        'checkin_time': attendance.checkin_time.strftime('%H:%M') if attendance and attendance.checkin_time else None,
        'classes': [
            {
                'id': c.course.id,
                'title': c.course.title,
                'status': c.status,
                'status_label': c.get_status_display(),
                'age_group_label': c.course.get_age_group_display(),
            }
            for c in courses
        ],
    }


def _get_own_child(request, child_id):
    """A member may only read and check in their own child."""
    child_ids = _my_child_ids(request.user)
    if not child_ids:
        return None
    return Child.objects.filter(pk=child_id, pk__in=child_ids).select_related('parent').first()


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def children_view(request):
    member = get_member(request.user)
    qs = member.children.select_related('parent').all() if member else Child.objects.none()
    search = (request.GET.get('search') or '').strip()
    if search:
        from django.db.models import Q
        qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))
    results = [_child_payload(request, ch) for ch in qs[:MAX_LIST]]
    return JsonResponse({'results': results, 'count': qs.count()})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def child_detail_view(request, child_id):
    child = _get_own_child(request, child_id)
    if child is None:
        return JsonResponse({'error': 'Child not found'}, status=404)
    return JsonResponse({'child': _child_payload(request, child)})


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def child_checkin_view(request, child_id):
    child = _get_own_child(request, child_id)
    if child is None:
        return JsonResponse({'error': 'Child not found'}, status=404)
    today = timezone.localdate()
    attendance, _ = ChildAttendance.objects.get_or_create(child=child, date=today)
    attendance.checked_in = True
    attendance.checkin_time = timezone.localtime().time().replace(microsecond=0)
    attendance.checked_in_by = get_member(request.user)
    attendance.save()
    return JsonResponse({'ok': True, 'child': _child_payload(request, child)})


@csrf_exempt
@token_required
@require_http_methods(['POST'])
def child_checkout_view(request, child_id):
    child = _get_own_child(request, child_id)
    if child is None:
        return JsonResponse({'error': 'Child not found'}, status=404)
    today = timezone.localdate()
    attendance, _ = ChildAttendance.objects.get_or_create(child=child, date=today)
    if not attendance.checked_in:
        return JsonResponse({'error': 'This child is not checked in today'}, status=400)
    attendance.checked_out = True
    attendance.checkout_time = timezone.localtime().time().replace(microsecond=0)
    attendance.checked_out_by = get_member(request.user)
    attendance.save()
    return JsonResponse({'ok': True, 'child': _child_payload(request, child)})


# ---------------------------------------------------------------------------
# Giving
# ---------------------------------------------------------------------------

@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def give_view(request):
    """Submit an online offering from the app."""
    member = get_member(request.user)
    if request.method == 'GET':
        qs = member.online_givings.all() if member else OnlineGiving.objects.none()
        return JsonResponse({
            'results': [_online_giving_payload(g) for g in qs[:MAX_LIST]],
            'count': qs.count(),
        })
    data = _json_body(request)
    try:
        # Money is handled as a Decimal so the amount is never stored as a float.
        amount = Decimal(str(data.get('amount') or 0)).quantize(Decimal('0.01'))
    except (TypeError, ValueError, ArithmeticError, InvalidOperation):
        return JsonResponse({'error': 'Enter a valid amount'}, status=400)
    if amount <= 0:
        return JsonResponse({'error': 'Enter an amount greater than zero'}, status=400)
    category = data.get('giving_category') or 'offering'
    valid = [c[0] for c in Giving.GIVING_CATEGORIES]
    if category not in valid:
        return JsonResponse({'error': 'Choose a valid giving category'}, status=400)
    frequency = data.get('frequency') or 'one_time'
    if frequency not in [f[0] for f in OnlineGiving.FREQUENCY_CHOICES]:
        frequency = 'one_time'
    email = (data.get('email') or (member.email if member else '') or '').strip()
    name = (data.get('name') or (str(member) if member else '') or '').strip()
    if not name:
        return JsonResponse({'error': 'Please enter your name'}, status=400)
    record = OnlineGiving.objects.create(
        name=name[:200],
        email=email,
        amount=amount,
        giving_category=category,
        frequency=frequency,
        note=(data.get('note') or '').strip(),
    )
    record.post_to_finance()
    return JsonResponse({'ok': True, 'giving': _online_giving_payload(record)}, status=201)


def _online_giving_payload(g):
    return {
        'id': g.id,
        'name': g.name,
        'email': g.email,
        'amount': str(g.amount),
        'giving_category': g.giving_category,
        'giving_category_label': g.get_giving_category_display(),
        'frequency': g.frequency,
        'frequency_label': g.get_frequency_display(),
        'reference_number': g.reference_number,
        'status': g.status,
        'status_label': g.get_status_display(),
        'created_at': g.created_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# Directory: members, ministries, all groups
# ---------------------------------------------------------------------------

def _directory_member_payload(request, member):
    """Limited view for the member directory: no address, no emergency contacts."""
    return {
        'id': member.id,
        # str(member) would append the member number, so build the name plainly.
        'full_name': '%s %s' % (member.first_name, member.last_name),
        'first_name': member.first_name,
        'last_name': member.last_name,
        'member_number': member.member_number,
        'phone': member.phone,
        'email': member.email,
        'gender': member.gender,
        'gender_label': member.get_gender_display() if hasattr(member, 'get_gender_display') else '',
        'membership_status': member.membership_status,
        'membership_status_label': member.get_membership_status_display(),
        'photo_url': _photo_url(request, member.photo) if hasattr(member, 'photo') else None,
    }


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def member_directory_view(request):
    qs = Member.objects.filter(membership_status='active')
    search = (request.GET.get('search') or '').strip()
    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
            | Q(member_number__icontains=search) | Q(phone__icontains=search)
        )
    qs = qs.order_by('first_name', 'last_name')
    return JsonResponse({
        'results': [_directory_member_payload(request, m) for m in qs[:MAX_LIST]],
        'count': qs.count(),
    })


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def member_directory_detail_view(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    payload = _directory_member_payload(request, member)
    payload['family'] = str(member.family) if member.family_id else None
    return JsonResponse({'member': payload})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def ministries_view(request):
    qs = Ministry.objects.filter(is_active=True)
    search = (request.GET.get('search') or '').strip()
    if search:
        qs = qs.filter(name__icontains=search)
    qs = qs.order_by('name')
    return JsonResponse({
        'results': [
            {
                'id': m.id,
                'name': m.name,
                'description': m.description,
                'leader': str(m.leader) if m.leader_id else None,
'purpose': '',
                'image_url': _photo_url(request, m.image) if hasattr(m, 'image') else None,
            }
            for m in qs[:MAX_LIST]
        ],
        'count': qs.count(),
    })


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def ministry_detail_view(request, ministry_id):
    ministry = get_object_or_404(Ministry, pk=ministry_id)
    members = ministry.members.filter(membership_status='active').order_by('first_name', 'last_name') \
        if hasattr(ministry, 'members') else Member.objects.none()
    return JsonResponse({
        'ministry': {
            'id': ministry.id,
            'name': ministry.name,
            'description': ministry.description,
            'leader': str(ministry.leader) if ministry.leader_id else None,
'purpose': '',
            'image_url': _photo_url(request, ministry.image) if hasattr(ministry, 'image') else None,
            'members': [_directory_member_payload(request, m) for m in members[:MAX_LIST]],
        }
    })


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def groups_browse_view(request):
    """All groups, not just mine, so members can find a fellowship to join."""
    qs = Group.objects.filter(is_active=True)
    search = (request.GET.get('search') or '').strip()
    if search:
        from django.db.models import Q
        qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
    qs = qs.order_by('name')
    return JsonResponse({
        'results': [_group_payload(g) for g in qs[:MAX_LIST]],
        'count': qs.count(),
    })


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def group_detail_view(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    payload = _group_payload(group)
    members = group.members.all().order_by('first_name', 'last_name')
    payload['members'] = [
        {
            'id': m.id,
            'full_name': '%s %s' % (m.first_name, m.last_name),
            'phone': m.phone,
            'email': m.email,
        }
        for m in members[:MAX_LIST]
    ]
    return JsonResponse({'group': payload})


# ---------------------------------------------------------------------------
# Facilities
# ---------------------------------------------------------------------------

@csrf_exempt
@token_required
@require_http_methods(['GET', 'POST'])
def facilities_view(request):
    if request.method == 'POST':
        member = get_member(request.user)
        if member is None:
            return JsonResponse({'error': 'No member profile linked to your account'}, status=400)
        data = _json_body(request)
        facility = get_object_or_404(Facility, pk=data.get('facility'))
        event_name = (data.get('event_name') or '').strip()
        purpose = (data.get('purpose') or '').strip()
        if not event_name:
            return JsonResponse({'error': 'Please give the booking a name'}, status=400)
        start_time = (data.get('start_time') or '').strip()
        end_time = (data.get('end_time') or '').strip()
        if not start_time or not end_time:
            return JsonResponse({'error': 'Start and end time are required'}, status=400)
        from datetime import date as date_cls, time as time_cls
        try:
            booking_date = date_cls.fromisoformat(
                (data.get('date') or '').strip() or str(timezone.localdate()))
            parsed_start = time_cls.fromisoformat(start_time)
            parsed_end = time_cls.fromisoformat(end_time)
        except ValueError:
            return JsonResponse({'error': 'Enter a valid date and time'}, status=400)
        if parsed_end <= parsed_start:
            return JsonResponse({'error': 'End time must be after the start time'}, status=400)
        booking = FacilityBooking.objects.create(
            facility=facility,
            booked_by=member,
            event_name=event_name[:200],
            date=booking_date,
            start_time=parsed_start,
            end_time=parsed_end,
            purpose=purpose,
        )
        return JsonResponse({'ok': True, 'booking': _booking_payload(booking)}, status=201)
    qs = Facility.objects.filter(is_available=True).order_by('name')
    return JsonResponse({
        'results': [
            {
                'id': f.id,
                'name': f.name,
                'description': f.description,
                'capacity': f.capacity,
                'location': f.location,
                'is_available': f.is_available,
            }
            for f in qs[:MAX_LIST]
        ],
        'count': qs.count(),
    })


def _booking_payload(b):
    return {
        'id': b.id,
        'facility': str(b.facility),
        'event_name': b.event_name,
        'date': b.date.isoformat(),
        'start_time': b.start_time.strftime('%H:%M'),
        'end_time': b.end_time.strftime('%H:%M'),
        'purpose': b.purpose,
        'status': b.status,
        'status_label': b.get_status_display(),
    }


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def my_bookings_view(request):
    member = get_member(request.user)
    qs = FacilityBooking.objects.filter(booked_by=member).select_related('facility') if member \
        else FacilityBooking.objects.none()
    return JsonResponse({
        'results': [_booking_payload(b) for b in qs[:MAX_LIST]],
        'count': qs.count(),
    })


# ---------------------------------------------------------------------------
# Detail endpoints the app was missing
# ---------------------------------------------------------------------------

@csrf_exempt
@token_required
@require_http_methods(['GET'])
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return JsonResponse({'event': _event_payload(request, event)})


@csrf_exempt
@token_required
@require_http_methods(['GET'])
def service_detail_view(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    member = get_member(request.user)
    payload = _service_payload(service, member.id if member else None)
    payload['notes'] = service.notes
    return JsonResponse({'service': payload})