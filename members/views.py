from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from accounts.models import User
from .forms import MemberForm, FamilyForm, MemberLoginForm
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = context['member']
        if member.user:
            context['login_form'] = MemberLoginForm(
                initial={'action': 'link', 'age_group': member.user.age_group}, member=member,
            )
        else:
            context['login_form'] = MemberLoginForm(member=member)
        return context


@login_required
def member_login(request, pk):
    """Create a login for a member or link an existing account to them."""
    member = get_object_or_404(Member, pk=pk)
    if not (request.user.is_admin_user or request.user.is_leader):
        messages.error(request, 'You do not have permission to manage member logins.')
        return redirect('members:member-detail', pk=member.pk)
    if request.method == 'POST':
        form = MemberLoginForm(request.POST, member=member)
        if form.is_valid():
            action = form.cleaned_data.get('action') or 'create'
            age_group = form.cleaned_data.get('age_group') or ''
            if action == 'link':
                user = form.cleaned_data.get('existing_user')
                linked_to = getattr(user, 'member_profile', None) if user else None
                if user is None:
                    messages.error(request, 'Please choose the user account to link.')
                elif linked_to is not None and linked_to.pk != member.pk:
                    messages.error(request, 'That account is already linked to another member.')
                else:
                    if member.user_id and member.user_id != user.pk:
                        member.user = None
                        member.save(update_fields=['user'])
                    member.user = user
                    member.save(update_fields=['user'])
                    user.age_group = age_group
                    user.save(update_fields=['age_group'])
                    messages.success(request, 'Linked account %s to this member.' % user.username)
            else:
                username = (form.cleaned_data.get('username') or '').strip()
                if not username:
                    messages.error(request, 'Please enter a username for the new login.')
                elif User.objects.filter(username__iexact=username).exists():
                    messages.error(request, 'That username is already taken.')
                else:
                    user = User.objects.create_user(
                        username=username,
                        email=member.email,
                        password=None,
                        first_name=member.first_name,
                        last_name=member.last_name,
                        role='member',
                        age_group=age_group,
                    )
                    member.user = user
                    member.save(update_fields=['user'])
                    messages.success(
                        request,
                        'Login %s created. Set a password from Accounts > Users before they sign in.' % user.username,
                    )
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('members:member-detail', pk=member.pk)


@login_required
def member_unlink_login(request, pk):
    """Remove the login link from a member (the account itself is kept)."""
    member = get_object_or_404(Member, pk=pk)
    if not (request.user.is_admin_user or request.user.is_leader):
        messages.error(request, 'You do not have permission to manage member logins.')
        return redirect('members:member-detail', pk=member.pk)
    if request.method == 'POST' and member.user:
        username = member.user.username
        member.user = None
        member.save(update_fields=['user'])
        messages.success(request, 'Login link removed from %s (account %s kept).' % (member, username))
    return redirect('members:member-detail', pk=member.pk)


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
