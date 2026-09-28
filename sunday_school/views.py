from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.models import User
from accounts.views import ContentWriteMixin
from children.models import Child
from members.models import Member
from .forms import AddChildForm, AddChildrenForm, CourseCommentForm, SundaySchoolCourseForm, TargetAgeGroupForm, TargetMinistryForm
from .models import CourseComment, CourseEnrollment, SundaySchoolCourse


class CourseListView(LoginRequiredMixin, ListView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('comments').annotate(
            approved_count=Count('enrollments', filter=Q(enrollments__status='approved')),
        ).order_by('-lesson_date', '-created_at')
        if not self.request.user.can_manage_content:
            queryset = queryset.filter(is_active=True)
        search = self.request.GET.get('search', '').strip()
        age_group = self.request.GET.get('age_group', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(scripture__icontains=search)
                | Q(lesson__icontains=search)
            )
        if age_group:
            queryset = queryset.filter(age_group=age_group)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['age_group'] = self.request.GET.get('age_group', '')
        context['age_groups'] = SundaySchoolCourse.AGE_GROUP_CHOICES
        page_ids = [c.pk for c in context['courses']]
        my_enrollments = {
            e.course_id: e
            for e in self.request.user.sunday_school_enrollments.filter(course_id__in=page_ids)
        }
        # A child's enrolment belongs to the parent's account, so the parent sees the class.
        member = Member.objects.filter(user=self.request.user).first()
        child_ids = list(member.children.values_list('pk', flat=True)) if member else []
        if child_ids:
            for e in CourseEnrollment.objects.filter(
                child_id__in=child_ids, course_id__in=page_ids,
            ).select_related('child'):
                my_enrollments.setdefault(e.course_id, e)
        context['my_enrollments'] = my_enrollments
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('enrollments__student', 'enrollments__child__parent')
        if not self.request.user.can_manage_content:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['comments'] = course.comments.select_related('user')
        context['comment_form'] = CourseCommentForm()
        context['can_view_attachments'] = self.request.user.is_admin_user
        if self.request.user.can_manage_content:
            enrollments = list(course.enrollments.all())
            context['pending_enrollments'] = [e for e in enrollments if e.status == 'pending']
            context['approved_enrollments'] = [e for e in enrollments if e.status == 'approved']
            context['child_count'] = sum(1 for e in enrollments if e.is_child)
            context['adult_count'] = sum(1 for e in enrollments if not e.is_child)
            context['add_child_form'] = AddChildForm(course=course)
            context['add_children_form'] = AddChildrenForm(course=course)
            context['add_ministry_form'] = TargetMinistryForm()
            context['add_age_group_form'] = TargetAgeGroupForm()
            context['my_enrollment'] = None
        else:
            # A parent sees the lesson when one of their children is on the class.
            member = Member.objects.filter(user=self.request.user).first()
            child_ids = list(member.children.values_list('pk', flat=True)) if member else []
            context['my_children'] = (
                Child.objects.filter(pk__in=child_ids, is_active=True) if child_ids else Child.objects.none()
            )
            context['my_enrollment'] = course.enrollments.filter(
                Q(student=self.request.user) | Q(child_id__in=child_ids)
            ).first()
        context['can_view_content'] = (
            self.request.user.can_manage_content
            or not course.enable_registration
            or (context['my_enrollment'] and context['my_enrollment'].status == 'approved')
        )
        return context


def children_in_age_group(age_group):
    """Active children whose age falls in the given Sunday School age group."""
    return [child for child in Child.objects.filter(is_active=True).select_related('parent')
            if child.age_group == age_group]


def add_children_to_course(course, children):
    """Add the given children to a course, skipping duplicates and respecting capacity.

    Returns (added, already_enrolled, skipped_full)."""
    added = 0
    already = 0
    skipped_full = 0
    for child in children:
        if CourseEnrollment.objects.filter(course=course, child=child).exists():
            already += 1
            continue
        if course.is_full:
            skipped_full += 1
            continue
        CourseEnrollment.objects.create(
            course=course, child=child,
            status='approved', approved_at=timezone.now(),
        )
        added += 1
    return added, already, skipped_full


def add_ministry_to_course(course, ministry):
    """Add the children of every member in the ministry."""
    children = Child.objects.filter(
        parent__in=ministry.members.all(), is_active=True,
    ).select_related('parent')
    return add_children_to_course(course, children)


def add_age_group_to_course(course, age_group):
    """Add every child whose age falls in the given group."""
    return add_children_to_course(course, children_in_age_group(age_group))


def report_added(request, added, already=0, skipped_full=0, subject='class', noun='child'):
    if added:
        note = '%d %s(s) added to the %s.' % (added, noun, subject)
        if skipped_full:
            note += ' %d not added because the class is full.' % skipped_full
        messages.success(request, note)
    elif already:
        messages.info(request, 'Those %ss are already in the %s.' % (noun, subject))
    else:
        messages.error(request, 'No %ss were added to the %s.' % (noun, subject))


class CourseRosterMixin:
    """Applies the optional 'add children' fields on the course form."""

    def apply_roster_additions(self, form, course):
        added, already, skipped = 0, 0, 0
        ministry = form.cleaned_data.get('add_ministry')
        if ministry:
            a, al, sk = add_ministry_to_course(course, ministry)
            added += a
            already += al
            skipped += sk
        age_group = form.cleaned_data.get('add_age_group')
        if age_group:
            a, al, sk = add_age_group_to_course(course, age_group)
            added += a
            already += al
            skipped += sk
        picked = form.cleaned_data.get('add_children')
        if picked:
            a, al, sk = add_children_to_course(course, picked)
            added += a
            already += al
            skipped += sk
        if ministry or age_group or list(picked or []):
            report_added(self.request, added, already, skipped, 'class')
        return added


class CourseCreateView(LoginRequiredMixin, ContentWriteMixin, CourseRosterMixin, CreateView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_form.html'
    form_class = SundaySchoolCourseForm
    success_url = reverse_lazy('sunday_school:course_list')

    def get_success_url(self):
        # land on the new course so the teacher can add / target members straight away
        return reverse('sunday_school:course_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, 'Course posted successfully.')
        response = super().form_valid(form)
        self.apply_roster_additions(form, self.object)
        return response


class CourseUpdateView(LoginRequiredMixin, ContentWriteMixin, CourseRosterMixin, UpdateView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_form.html'
    form_class = SundaySchoolCourseForm
    success_url = reverse_lazy('sunday_school:course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully.')
        response = super().form_valid(form)
        self.apply_roster_additions(form, self.object)
        return response


class CourseDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_confirm_delete.html'
    context_object_name = 'course'
    success_url = reverse_lazy('sunday_school:course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Course deleted successfully.')
        return super().form_valid(form)


@login_required
def add_comment(request, pk):
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not course.is_active and not request.user.can_manage_content:
        raise Http404
    if request.method == 'POST':
        form = CourseCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.course = course
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been posted.')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def delete_comment(request, pk, comment_id):
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    comment = get_object_or_404(CourseComment, pk=comment_id, course=course)
    if request.method == 'POST' and (request.user.is_admin_user or comment.user == request.user):
        comment.delete()
        messages.success(request, 'Comment removed.')
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def delete_attachment(request, pk, attachment):
    """Teacher-only removal of a course material (video/pdf/audio/link)."""
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers and administrators can remove course materials.')
        return redirect('sunday_school:course_detail', pk=pk)
    if attachment not in ('video', 'pdf_attachment', 'audio', 'video_url'):
        messages.error(request, 'Unknown course material.')
        return redirect('sunday_school:course_detail', pk=pk)
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if request.method == 'POST':
        field = getattr(course, attachment, None)
        if field:
            if hasattr(field, 'delete'):
                field.delete(save=False)
            setattr(course, attachment, '')
            course.save(update_fields=[attachment])
            messages.success(request, 'Course material removed.')
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def add_child(request, pk):
    """Teacher hand-picks a child and adds them to the class directly."""
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can add children to the class.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    if request.method == 'POST':
        form = AddChildForm(request.POST, course=course)
        if form.is_valid():
            child = form.cleaned_data['child']
            if course.is_full:
                messages.error(request, 'Class is full, cannot add more children.')
            else:
                CourseEnrollment.objects.get_or_create(
                    course=course, child=child,
                    defaults={'status': 'approved', 'approved_at': timezone.now()},
                )
                messages.success(request, '%s added to the class.' % child.get_full_name())
        else:
            messages.error(request, 'Please select a valid child.')
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def add_children(request, pk):
    """Teacher picks several children at once (families, classes, groups)."""
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can add children to the class.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    if request.method == 'POST':
        form = AddChildrenForm(request.POST, course=course)
        if form.is_valid():
            picked = list(form.cleaned_data['children'])
            if not picked:
                messages.error(request, 'No children selected.')
            elif course.spots_left == 0:
                messages.error(request, 'Class is full, cannot add more children.')
            else:
                added, already, skipped = add_children_to_course(course, picked)
                if already:
                    messages.info(request, '%d child(ren) were already in the class.' % already)
                report_added(request, added, already, skipped, 'class')
        else:
            messages.error(request, 'Please select valid children.')
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def add_ministry(request, pk):
    """Teacher targets a whole ministry - the children of its members join."""
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can add children to the class.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    if request.method == 'POST':
        form = TargetMinistryForm(request.POST)
        if form.is_valid():
            ministry = form.cleaned_data['ministry']
            added, already, skipped = add_ministry_to_course(course, ministry)
            if added:
                messages.success(
                    request,
                    '%d child(ren) of %s added to the class.' % (added, ministry.name),
                )
            elif already:
                messages.info(request, 'The children of %s are already in the class.' % ministry.name)
            else:
                messages.error(
                    request,
                    'No children are registered under the members of %s yet.' % ministry.name,
                )
        else:
            messages.error(request, 'Please select a valid ministry.')
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def add_age_group(request, pk):
    """Teacher targets a whole age group of children."""
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can add children to the class.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    if request.method == 'POST':
        form = TargetAgeGroupForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['age_group']
            label = dict(SundaySchoolCourse.AGE_GROUP_CHOICES)[group]
            added, already, skipped = add_age_group_to_course(course, group)
            if added:
                messages.success(request, '%d child(ren) in %s added to the class.' % (added, label))
            elif already:
                messages.info(request, 'All children in %s are already in the class.' % label)
            else:
                messages.error(
                    request,
                    'No children fall in %s yet. Add children and check their date of birth.' % label,
                )
        else:
            messages.error(request, 'Please select a valid age group.')
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def join_course(request, pk):
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not course.is_active and not request.user.can_manage_content:
        raise Http404
    if request.user.can_manage_content:
        messages.error(request, 'Teachers manage the class instead of joining it.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    if not course.enable_registration:
        messages.error(request, 'Enrollment for this class is not open.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    enrollment, created = CourseEnrollment.objects.get_or_create(
        course=course, student=request.user,
    )
    if not created:
        if enrollment.status == 'approved':
            messages.info(request, 'You are already a member of this class.')
            return redirect('sunday_school:course_detail', pk=course.pk)
        if enrollment.status == 'pending':
            messages.info(request, 'Your request is still waiting for the teacher\'s approval.')
            return redirect('sunday_school:course_detail', pk=course.pk)
        enrollment.status = 'pending'
        enrollment.approved_at = None
        enrollment.save(update_fields=['status', 'approved_at'])
    if course.is_full:
        if created:
            enrollment.delete()
        messages.error(request, 'Sorry, this class is already full.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    if course.requires_approval:
        messages.success(request, 'Join request sent. The teacher will review it.')
    else:
        enrollment.status = 'approved'
        enrollment.approved_at = timezone.now()
        enrollment.save(update_fields=['status', 'approved_at'])
        messages.success(request, 'You have joined this class!')
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def leave_course(request, pk):
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if request.method == 'POST':
        CourseEnrollment.objects.filter(course=course, student=request.user).delete()
        messages.success(request, 'You have left this class.')
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def approve_enrollment(request, pk, enrollment_id):
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can approve join requests.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    enrollment = get_object_or_404(CourseEnrollment, pk=enrollment_id, course=course)
    if request.method == 'POST':
        if enrollment.status == 'pending' and course.is_full:
            messages.error(request, 'Class is full, cannot approve more students.')
        else:
            enrollment.status = 'approved'
            enrollment.approved_at = timezone.now()
            enrollment.save(update_fields=['status', 'approved_at'])
            messages.success(request, '%s is now in the class.' % enrollment.student_name)
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def reject_enrollment(request, pk, enrollment_id):
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can reject join requests.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    enrollment = get_object_or_404(CourseEnrollment, pk=enrollment_id, course=course)
    if request.method == 'POST':
        enrollment.status = 'rejected'
        enrollment.save(update_fields=['status'])
        messages.success(request, 'Request from %s rejected.' % enrollment.student_name)
    return redirect('sunday_school:course_detail', pk=course.pk)


@login_required
def remove_enrollment(request, pk, enrollment_id):
    course = get_object_or_404(SundaySchoolCourse, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can remove students from the class.')
        return redirect('sunday_school:course_detail', pk=course.pk)
    enrollment = get_object_or_404(CourseEnrollment, pk=enrollment_id, course=course)
    if request.method == 'POST':
        name = enrollment.student_name
        enrollment.delete()
        messages.success(request, '%s removed from the class.' % name)
    return redirect('sunday_school:course_detail', pk=course.pk)