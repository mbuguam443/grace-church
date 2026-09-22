from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.views import ContentWriteMixin
from .models import BibleStudyNote


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
