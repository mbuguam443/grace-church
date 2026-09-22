from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import MemberForm, FamilyForm
from .models import Member, Family


class WriteAccessMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_admin_user or user.is_leader

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to perform this action.')
        return super().handle_no_permission()


class MemberListView(LoginRequiredMixin, ListView):
    model = Member
    template_name = 'members/member_list.html'
    context_object_name = 'members'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        gender = self.request.GET.get('gender', '').strip()

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(middle_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone__icontains=search)
                | Q(email__icontains=search)
                | Q(member_number__icontains=search)
            )
        if status:
            queryset = queryset.filter(membership_status=status)
        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['gender_filter'] = self.request.GET.get('gender', '')
        context['status_choices'] = Member.STATUS_CHOICES
        context['gender_choices'] = [('male', 'Male'), ('female', 'Female')]
        return context


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
    template_name = 'members/member_detail.html'
    context_object_name = 'member'


class MemberCreateView(LoginRequiredMixin, WriteAccessMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = 'members/member_form.html'
    success_url = reverse_lazy('members:member-list')

    def form_valid(self, form):
        messages.success(self.request, 'Member created successfully.')
        return super().form_valid(form)


class MemberUpdateView(LoginRequiredMixin, WriteAccessMixin, UpdateView):
    model = Member
    form_class = MemberForm
    template_name = 'members/member_form.html'
    success_url = reverse_lazy('members:member-list')

    def form_valid(self, form):
        messages.success(self.request, 'Member updated successfully.')
        return super().form_valid(form)


class MemberDeleteView(LoginRequiredMixin, WriteAccessMixin, DeleteView):
    model = Member
    template_name = 'members/member_confirm_delete.html'
    context_object_name = 'member'
    success_url = reverse_lazy('members:member-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Member deleted successfully.')
        return super().delete(request, *args, **kwargs)


class FamilyListView(LoginRequiredMixin, ListView):
    model = Family
    template_name = 'members/family_list.html'
    context_object_name = 'families'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(phone__icontains=search)
                | Q(email__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class FamilyDetailView(LoginRequiredMixin, DetailView):
    model = Family
    template_name = 'members/family_detail.html'
    context_object_name = 'family'


class FamilyCreateView(LoginRequiredMixin, WriteAccessMixin, CreateView):
    model = Family
    form_class = FamilyForm
    template_name = 'members/family_form.html'
    success_url = reverse_lazy('members:family-list')

    def form_valid(self, form):
        messages.success(self.request, 'Family created successfully.')
        return super().form_valid(form)


class FamilyUpdateView(LoginRequiredMixin, WriteAccessMixin, UpdateView):
    model = Family
    form_class = FamilyForm
    template_name = 'members/family_form.html'
    success_url = reverse_lazy('members:family-list')

    def form_valid(self, form):
        messages.success(self.request, 'Family updated successfully.')
        return super().form_valid(form)


class FamilyDeleteView(LoginRequiredMixin, WriteAccessMixin, DeleteView):
    model = Family
    template_name = 'members/family_confirm_delete.html'
    context_object_name = 'family'
    success_url = reverse_lazy('members:family-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Family deleted successfully.')
        return super().delete(request, *args, **kwargs)
