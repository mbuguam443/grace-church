from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.views import ContentWriteMixin
from .forms import AddStudentForm, AddStudentsForm, BibleStudyCommentForm, BibleStudyNoteForm, TargetMinistryForm
from .models import BibleStudyComment, BibleStudyEnrollment, BibleStudyNote


class BibleStudyListView(LoginRequiredMixin, ListView):
    model = BibleStudyNote
    template_name = 'bible_study/study_list.html'
    context_object_name = 'studies'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('comments').annotate(
            approved_count=Count('enrollments', filter=Q(enrollments__status='approved')),
        ).order_by('-study_date')
        if not self.request.user.can_manage_content:
            queryset = queryset.filter(is_active=True)
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(bible_verse__icontains=search)
                | Q(teacher__icontains=search)
                | Q(content__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        page_ids = [s.pk for s in context['studies']]
        my = {
            e.study_id: e
            for e in self.request.user.bible_study_enrollments.filter(study_id__in=page_ids)
        }
        context['my_enrollments'] = my
        return context


class BibleStudyDetailView(LoginRequiredMixin, DetailView):
    model = BibleStudyNote
    template_name = 'bible_study/study_detail.html'
    context_object_name = 'study'

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('enrollments__student')
        if not self.request.user.can_manage_content:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        study = self.get_object()
        context['comments'] = study.comments.select_related('user')
        context['comment_form'] = BibleStudyCommentForm()
        context['can_view_attachments'] = self.request.user.is_admin_user
        if self.request.user.can_manage_content:
            enrollments = list(study.enrollments.all())
            context['pending_enrollments'] = [e for e in enrollments if e.status == 'pending']
            context['approved_enrollments'] = [e for e in enrollments if e.status == 'approved']
            context['add_student_form'] = AddStudentForm(study=study)
            context['add_students_form'] = AddStudentsForm(study=study)
            context['add_ministry_form'] = TargetMinistryForm()
            context['my_enrollment'] = None
        else:
            context['my_enrollment'] = study.enrollments.filter(student=self.request.user).first()
        context['can_view_content'] = (
            self.request.user.can_manage_content
            or not study.enable_registration
            or (context['my_enrollment'] and context['my_enrollment'].status == 'approved')
        )
        return context


@login_required
def add_comment(request, pk):
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if not study.is_active and not request.user.can_manage_content:
        raise Http404
    if request.method == 'POST':
        form = BibleStudyCommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.study = study
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been posted.')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def delete_comment(request, pk, comment_id):
    study = get_object_or_404(BibleStudyNote, pk=pk)
    comment = get_object_or_404(BibleStudyComment, pk=comment_id, study=study)
    if request.method == 'POST' and (request.user.is_admin_user or comment.user == request.user):
        comment.delete()
        messages.success(request, 'Comment removed.')
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def delete_attachment(request, pk, attachment):
    """Teacher-only removal of a study material (video/pdf/audio/link)."""
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers and administrators can remove study materials.')
        return redirect('bible_study:study_detail', pk=pk)
    if attachment not in ('video', 'pdf_attachment', 'audio', 'video_url'):
        messages.error(request, 'Unknown study material.')
        return redirect('bible_study:study_detail', pk=pk)
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if request.method == 'POST':
        field = getattr(study, attachment, None)
        if field:
            if hasattr(field, 'delete'):
                field.delete(save=False)
            setattr(study, attachment, '')
            study.save(update_fields=[attachment])
            messages.success(request, 'Study material removed.')
    return redirect('bible_study:study_detail', pk=study.pk)


class BibleStudyCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = BibleStudyNote
    template_name = 'bible_study/study_form.html'
    form_class = BibleStudyNoteForm
    success_url = reverse_lazy('bible_study:study_list')

    def form_valid(self, form):
        messages.success(self.request, 'Bible study note posted successfully.')
        return super().form_valid(form)


class BibleStudyUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = BibleStudyNote
    template_name = 'bible_study/study_form.html'
    form_class = BibleStudyNoteForm
    success_url = reverse_lazy('bible_study:study_list')

    def form_valid(self, form):
        messages.success(self.request, 'Bible study note updated successfully.')
        return super().form_valid(form)


class BibleStudyDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = BibleStudyNote
    template_name = 'bible_study/study_confirm_delete.html'
    success_url = reverse_lazy('bible_study:study_list')

    def form_valid(self, form):
        messages.success(self.request, 'Bible study note deleted successfully.')
        return super().form_valid(form)


@login_required
def add_student(request, pk):
    """Teacher hand-picks a member and adds them to the study directly."""
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can add students to the class.')
        return redirect('bible_study:study_detail', pk=study.pk)
    if request.method == 'POST':
        form = AddStudentForm(request.POST, study=study)
        if form.is_valid():
            student = form.cleaned_data['student']
            if study.is_full:
                messages.error(request, 'Class is full, cannot add more students.')
            else:
                BibleStudyEnrollment.objects.get_or_create(
                    study=study, student=student,
                    defaults={'status': 'approved', 'approved_at': timezone.now()},
                )
                messages.success(request, '%s added to the class.' % (student.get_full_name() or student.username))
        else:
            messages.error(request, 'Please select a valid member.')
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def add_students(request, pk):
    """Teacher picks several members at once (ministries-style) for a targeted class."""
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can add students to the class.')
        return redirect('bible_study:study_detail', pk=study.pk)
    if request.method == 'POST':
        form = AddStudentsForm(request.POST, study=study)
        if form.is_valid():
            picked = list(form.cleaned_data['students'])
            if not picked:
                messages.error(request, 'No members selected.')
            elif study.spots_left == 0:
                messages.error(request, 'Class is full, cannot add more students.')
            else:
                added = 0
                for student in picked:
                    if study.is_full:
                        break
                    BibleStudyEnrollment.objects.get_or_create(
                        study=study, student=student,
                        defaults={'status': 'approved', 'approved_at': timezone.now()},
                    )
                    added += 1
                if added >= len(picked):
                    messages.success(request, '%d member(s) added to the class.' % added)
                else:
                    messages.success(
                        request,
                        '%d member(s) added. Class is now full - %d not added.'
                        % (added, len(picked) - added),
                    )
        else:
            messages.error(request, 'Please select valid members.')
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def add_ministry(request, pk):
    """Teacher targets a whole ministry - all its members join the class."""
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can add students to the class.')
        return redirect('bible_study:study_detail', pk=study.pk)
    if request.method == 'POST':
        form = TargetMinistryForm(request.POST)
        if form.is_valid():
            ministry = form.cleaned_data['ministry']
            added = 0
            already = 0
            no_user = 0
            for member in ministry.members.all().select_related('user'):
                if member.user is None:
                    no_user += 1
                    continue
                if BibleStudyEnrollment.objects.filter(study=study, student=member.user).exists():
                    already += 1
                    continue
                if study.is_full:
                    break
                BibleStudyEnrollment.objects.create(
                    study=study, student=member.user,
                    status='approved', approved_at=timezone.now(),
                )
                added += 1
            if added:
                messages.success(
                    request,
                    '%d member(s) from %s added to the class.' % (added, ministry.name),
                )
            elif already:
                messages.info(request, 'All members of %s are already in the class.' % ministry.name)
            elif no_user:
                messages.info(request, 'No members of %s have logins yet, so none could be added.' % ministry.name)
            else:
                messages.error(request, 'No members were added.')
        else:
            messages.error(request, 'Please select a valid ministry.')
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def join_study(request, pk):
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if not study.is_active and not request.user.can_manage_content:
        raise Http404
    if request.user.can_manage_content:
        messages.error(request, 'Teachers manage the class instead of joining it.')
        return redirect('bible_study:study_detail', pk=study.pk)
    if not study.enable_registration:
        messages.error(request, 'Enrollment for this class is not open.')
        return redirect('bible_study:study_detail', pk=study.pk)
    enrollment, created = BibleStudyEnrollment.objects.get_or_create(
        study=study, student=request.user,
    )
    if not created:
        if enrollment.status == 'approved':
            messages.info(request, 'You are already a member of this class.')
            return redirect('bible_study:study_detail', pk=study.pk)
        if enrollment.status == 'pending':
            messages.info(request, 'Your request is still waiting for the teacher\'s approval.')
            return redirect('bible_study:study_detail', pk=study.pk)
        enrollment.status = 'pending'
        enrollment.approved_at = None
        enrollment.save(update_fields=['status', 'approved_at'])
    if study.is_full:
        if created:
            enrollment.delete()
        messages.error(request, 'Sorry, this class is already full.')
        return redirect('bible_study:study_detail', pk=study.pk)
    if study.requires_approval:
        messages.success(request, 'Join request sent. The teacher will review it.')
    else:
        enrollment.status = 'approved'
        enrollment.approved_at = timezone.now()
        enrollment.save(update_fields=['status', 'approved_at'])
        messages.success(request, 'You have joined this class!')
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def leave_study(request, pk):
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if request.method == 'POST':
        BibleStudyEnrollment.objects.filter(study=study, student=request.user).delete()
        messages.success(request, 'You have left this class.')
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def approve_enrollment(request, pk, enrollment_id):
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can approve join requests.')
        return redirect('bible_study:study_detail', pk=study.pk)
    enrollment = get_object_or_404(BibleStudyEnrollment, pk=enrollment_id, study=study)
    if request.method == 'POST':
        if enrollment.status == 'pending' and study.is_full:
            messages.error(request, 'Class is full, cannot approve more students.')
        else:
            enrollment.status = 'approved'
            enrollment.approved_at = timezone.now()
            enrollment.save(update_fields=['status', 'approved_at'])
            messages.success(request, '%s is now in the class.' % enrollment.student_name)
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def reject_enrollment(request, pk, enrollment_id):
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can reject join requests.')
        return redirect('bible_study:study_detail', pk=study.pk)
    enrollment = get_object_or_404(BibleStudyEnrollment, pk=enrollment_id, study=study)
    if request.method == 'POST':
        enrollment.status = 'rejected'
        enrollment.save(update_fields=['status'])
        messages.success(request, 'Request from %s rejected.' % enrollment.student_name)
    return redirect('bible_study:study_detail', pk=study.pk)


@login_required
def remove_enrollment(request, pk, enrollment_id):
    study = get_object_or_404(BibleStudyNote, pk=pk)
    if not request.user.can_manage_content:
        messages.error(request, 'Only teachers can remove students from the class.')
        return redirect('bible_study:study_detail', pk=study.pk)
    enrollment = get_object_or_404(BibleStudyEnrollment, pk=enrollment_id, study=study)
    if request.method == 'POST':
        name = enrollment.student_name
        enrollment.delete()
        messages.success(request, '%s removed from the class.' % name)
    return redirect('bible_study:study_detail', pk=study.pk)
