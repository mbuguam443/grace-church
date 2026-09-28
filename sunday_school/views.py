from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.views import ContentWriteMixin
from .forms import CourseCommentForm, SundaySchoolCourseForm
from .models import CourseComment, SundaySchoolCourse


class CourseListView(LoginRequiredMixin, ListView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('comments')
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
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.can_manage_content:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['comments'] = course.comments.select_related('user')
        context['comment_form'] = CourseCommentForm()
        context['can_view_attachments'] = self.request.user.is_admin_user
        return context


class CourseCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_form.html'
    form_class = SundaySchoolCourseForm
    success_url = reverse_lazy('sunday_school:course_list')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, 'Course posted successfully.')
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_form.html'
    form_class = SundaySchoolCourseForm
    success_url = reverse_lazy('sunday_school:course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully.')
        return super().form_valid(form)


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