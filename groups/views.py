from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from accounts.views import ContentWriteMixin
from .models import Group, GroupAttendance


class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'groups/group_list.html'
    context_object_name = 'groups'


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'


class GroupCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Group
    template_name = 'groups/group_form.html'
    fields = ['name', 'description', 'leader', 'assistant_leader', 'meeting_day', 'meeting_time', 'location', 'members', 'is_active']
    success_url = reverse_lazy('groups:group-list')

    def form_valid(self, form):
        messages.success(self.request, 'Group created successfully.')
        return super().form_valid(form)


class GroupUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Group
    template_name = 'groups/group_form.html'
    fields = ['name', 'description', 'leader', 'assistant_leader', 'meeting_day', 'meeting_time', 'location', 'members', 'is_active']
    success_url = reverse_lazy('groups:group-list')

    def form_valid(self, form):
        messages.success(self.request, 'Group updated successfully.')
        return super().form_valid(form)


class GroupDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Group
    template_name = 'groups/group_confirm_delete.html'
    context_object_name = 'group'
    success_url = reverse_lazy('groups:group-list')

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Group deleted successfully.')
        return super().post(request, *args, **kwargs)


class GroupAttendanceView(LoginRequiredMixin, View):
    template_name = 'groups/group_attendance.html'

    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        attendances = group.group_attendances.all()
        context = {
            'group': group,
            'attendances': attendances,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        date = request.POST.get('date')
        notes = request.POST.get('notes', '')
        member_ids = request.POST.getlist('members')

        attendance = GroupAttendance.objects.create(
            group=group,
            date=date,
            notes=notes,
        )
        attendance.members.set(member_ids)
        messages.success(request, 'Attendance recorded successfully.')
        return redirect('groups:group-detail', pk=group.pk)
