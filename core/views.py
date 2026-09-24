from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import ChurchSetting, Leader


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_admin_user or self.request.user.is_leader)


class SettingsView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = ChurchSetting
    template_name = 'core/settings.html'
    fields = ['church_name', 'short_name', 'logo', 'favicon', 'hero_image', 'events_image',
              'sermons_image', 'cta_image', 'email', 'phone', 'address',
              'website', 'currency', 'timezone', 'primary_color', 'secondary_color',
              'accent_color', 'gold_color', 'audio_file', 'audio_title', 'audio_speaker',
              'service_times', 'about_history_intro', 'about_history_body',
              'about_history_image', 'about_call', 'about_divine_promise', 'about_milestones']

    def get_object(self):
        return ChurchSetting.get_settings()

    def form_valid(self, form):
        messages.success(self.request, 'Settings updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('core:settings')


class LeaderListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Leader
    template_name = 'core/leaders.html'
    context_object_name = 'leaders'
    paginate_by = 20

    def get_queryset(self):
        return Leader.objects.order_by('order', 'name')


class LeaderCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Leader
    template_name = 'core/leader_form.html'
    fields = ['name', 'role', 'photo', 'bio', 'order', 'is_active']

    def get_success_url(self):
        return reverse_lazy('core:leaders')

    def form_valid(self, form):
        messages.success(self.request, 'Leader added successfully.')
        return super().form_valid(form)


class LeaderUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Leader
    template_name = 'core/leader_form.html'
    fields = ['name', 'role', 'photo', 'bio', 'order', 'is_active']

    def get_success_url(self):
        return reverse_lazy('core:leaders')

    def form_valid(self, form):
        messages.success(self.request, 'Leader updated successfully.')
        return super().form_valid(form)


class LeaderDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Leader
    template_name = 'core/leader_confirm_delete.html'
    success_url = reverse_lazy('core:leaders')

    def form_valid(self, form):
        messages.success(self.request, 'Leader removed.')
        return super().form_valid(form)