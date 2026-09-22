from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from accounts.views import ContentWriteMixin
from .models import Song


class SongListView(LoginRequiredMixin, ListView):
    model = Song
    template_name = 'songs/song_list.html'
    context_object_name = 'songs'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category', '').strip()
        search = self.request.GET.get('search', '').strip()
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search) | Q(lyrics__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.request.GET.get('category', '')
        context['search'] = self.request.GET.get('search', '')
        context['categories'] = Song.CATEGORY_CHOICES
        return context


class SongDetailView(LoginRequiredMixin, DetailView):
    model = Song
    template_name = 'songs/song_detail.html'
    context_object_name = 'song'


class SongCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Song
    template_name = 'songs/song_form.html'
    fields = ['title', 'category', 'lyrics', 'author', 'scripture', 'key', 'tempo', 'youtube_url']
    success_url = reverse_lazy('songs:song_list')

    def form_valid(self, form):
        messages.success(self.request, 'Song posted successfully.')
        return super().form_valid(form)


class SongUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Song
    template_name = 'songs/song_form.html'
    fields = ['title', 'category', 'lyrics', 'author', 'scripture', 'key', 'tempo', 'youtube_url']
    success_url = reverse_lazy('songs:song_list')

    def form_valid(self, form):
        messages.success(self.request, 'Song updated successfully.')
        return super().form_valid(form)


class SongDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Song
    template_name = 'songs/song_confirm_delete.html'
    success_url = reverse_lazy('songs:song_list')

    def form_valid(self, form):
        messages.success(self.request, 'Song deleted successfully.')
        return super().form_valid(form)
