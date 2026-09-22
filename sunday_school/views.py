from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.views import ContentWriteMixin
from .models import SundaySchoolCourse


class CourseListView(LoginRequiredMixin, ListView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
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


class CourseCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_form.html'
    fields = ['title', 'age_group', 'lesson_date', 'scripture', 'memory_verse', 'lesson', 'activities', 'is_active']
    success_url = reverse_lazy('sunday_school:course_list')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, 'Course posted successfully.')
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = SundaySchoolCourse
    template_name = 'sunday_school/course_form.html'
    fields = ['title', 'age_group', 'lesson_date', 'scripture', 'memory_verse', 'lesson', 'activities', 'is_active']
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