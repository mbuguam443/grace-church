from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.views import ContentWriteMixin
from .forms import BibleStudyCommentForm
from .models import BibleStudyComment, BibleStudyNote


class BibleStudyListView(LoginRequiredMixin, ListView):
    model = BibleStudyNote
    template_name = 'bible_study/study_list.html'
    context_object_name = 'studies'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
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
        return context


class BibleStudyDetailView(LoginRequiredMixin, DetailView):
    model = BibleStudyNote
    template_name = 'bible_study/study_detail.html'
    context_object_name = 'study'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.can_manage_content:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        study = self.get_object()
        context['comments'] = study.comments.select_related('user')
        context['comment_form'] = BibleStudyCommentForm()
        context['can_view_attachments'] = self.request.user.is_admin_user
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


class BibleStudyCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = BibleStudyNote
    template_name = 'bible_study/study_form.html'
    fields = [
        'title', 'bible_verse', 'study_date', 'teacher', 'series',
        'content', 'key_points', 'prayer_points', 'discussion_questions', 'is_active',
    ]
    success_url = reverse_lazy('bible_study:study_list')

    def form_valid(self, form):
        messages.success(self.request, 'Bible study note posted successfully.')
        return super().form_valid(form)


class BibleStudyUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = BibleStudyNote
    template_name = 'bible_study/study_form.html'
    fields = [
        'title', 'bible_verse', 'study_date', 'teacher', 'series',
        'content', 'key_points', 'prayer_points', 'discussion_questions', 'is_active',
    ]
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
