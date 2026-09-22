from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import ChurchSetting


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_admin_user or self.request.user.is_leader)


class SettingsView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = ChurchSetting
    template_name = 'core/settings.html'
    fields = ['church_name', 'short_name', 'logo', 'favicon', 'hero_image', 'events_image',
              'sermons_image', 'cta_image', 'email', 'phone', 'address',
              'website', 'currency', 'timezone', 'primary_color', 'secondary_color',
              'accent_color', 'gold_color', 'service_times']

    def get_object(self):
        return ChurchSetting.get_settings()

    def form_valid(self, form):
        messages.success(self.request, 'Settings updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('core:settings')
