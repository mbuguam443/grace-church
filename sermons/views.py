from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView

from accounts.views import ContentWriteMixin
from .models import Sermon


class SermonListView(LoginRequiredMixin, ListView):
    model = Sermon
    template_name = 'sermons/sermon_list.html'
    context_object_name = 'sermons'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('q', '') or self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(speaker__icontains=search)
                | Q(bible_verse__icontains=search)
                | Q(description__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__iexact=category)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q', '') or self.request.GET.get('search', '')
        context['category'] = self.request.GET.get('category', '')
        context['categories'] = Sermon.CATEGORY_CHOICES
        return context


class SermonCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Sermon
    template_name = 'sermons/sermon_form.html'
    fields = [
        'title', 'speaker', 'date', 'bible_verse', 'series', 'category',
        'description', 'sermon_notes', 'youtube_url', 'audio_file', 'video_file', 'pdf_file',
    ]
    success_url = reverse_lazy('sermons:sermon_list')

    def form_valid(self, form):
        messages.success(self.request, 'Sermon posted successfully.')
        return super().form_valid(form)


class SermonUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Sermon
    template_name = 'sermons/sermon_form.html'
    fields = [
        'title', 'speaker', 'date', 'bible_verse', 'series', 'category',
        'description', 'sermon_notes', 'youtube_url', 'audio_file', 'video_file', 'pdf_file',
    ]
    success_url = reverse_lazy('sermons:sermon_list')

    def form_valid(self, form):
        messages.success(self.request, 'Sermon updated successfully.')
        return super().form_valid(form)


class SermonDetailView(LoginRequiredMixin, DetailView):
    model = Sermon
    template_name = 'sermons/sermon_detail.html'
    context_object_name = 'sermon'


class SermonDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Sermon
    template_name = 'sermons/sermon_confirm_delete.html'
    success_url = reverse_lazy('sermons:sermon_list')

    def form_valid(self, form):
        messages.success(self.request, 'Sermon deleted successfully.')
        return super().form_valid(form)
