import secrets
import string
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from .models import User
from .forms import UserRegistrationForm, UserUpdateForm, ProfileForm, MemberRegistrationForm
from core.models import RoleModulePermission
from core.modules import MODULES


def login_view(request):
    from django.contrib.auth.views import LoginView
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True)(request)


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_admin_user or self.request.user.is_superuser)


class MemberRegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return render(request, self.template_name, {'form': MemberRegistrationForm()})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            member = form.member
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                phone=(form.cleaned_data.get('phone') or '').strip(),
                first_name=member.first_name,
                last_name=member.last_name,
                role='member',
                is_active=False,
            )
            member.user = user
            member.save(update_fields=['user'])
            return render(request, 'accounts/register_success.html')
        return render(request, self.template_name, {'form': form})


class MemberApprovalView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = 'accounts/member_approval.html'

    def get(self, request):
        pending = User.objects.filter(is_active=False, role='member').select_related('member_profile').order_by('date_joined')
        return render(request, self.template_name, {'pending_users': pending})

    def post(self, request):
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        try:
            user = User.objects.get(pk=user_id, is_active=False, role='member')
        except User.DoesNotExist:
            messages.error(request, 'Pending registration not found.')
            return redirect('accounts:approval')
        if action == 'approve':
            user.is_active = True
            user.save(update_fields=['is_active'])
            self._send_approval_email(user)
            messages.success(request, f'{user.get_full_name() or user.username} has been approved.')
        elif action == 'reject':
            user.delete()
            messages.warning(request, f'{user.get_full_name() or user.username} was rejected and removed.')
        else:
            messages.error(request, 'Unknown action.')
        return redirect('accounts:approval')

    def _send_approval_email(self, user):
        try:
            subject = f'Your {settings.CHURCH_NAME} Account Has Been Approved'
            login_url = self.request.build_absolute_uri(reverse_lazy('accounts:login'))
            plain_message = (
                f'Hello {user.get_full_name() or user.username},\n\n'
                f'Your account for the {settings.CHURCH_NAME} Members Portal has been approved.\n\n'
                f'Username: {user.username}\n\n'
                f'You can now log in using your password at {login_url}.\n\n'
                f'Welcome to the family!\n{settings.CHURCH_NAME}'
            )
            send_mail(subject, plain_message, settings.CHURCH_EMAIL, [user.email], fail_silently=True)
        except Exception:
            pass


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


class ContentWriteMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_manage_content

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to perform this action.')
        return super().handle_no_permission()


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['super_admin', 'admin', 'pastor']

    def form_valid(self, form):
        password = self._generate_password()
        user = form.save(commit=False)
        user.password = make_password(password)
        user.save()

        self._send_credentials_email(user, password)

        messages.success(
            self.request,
            f'User "{user.username}" created successfully. '
            f'Credentials have been sent to {user.email}.'
        )
        return redirect(self.success_url)

    def _generate_password(self):
        alphabet = string.ascii_letters + string.digits + '!@#$%&*'
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%&*' for c in password)
        if not (has_upper and has_digit and has_special):
            return self._generate_password()
        return password

    def _send_credentials_email(self, user, password):
        try:
            subject = f'Your {settings.CHURCH_NAME} Account Credentials'
            html_message = render_to_string('accounts/email_credentials.html', {
                'user': user,
                'password': password,
                'church_name': settings.CHURCH_NAME,
                'login_url': self.request.build_absolute_uri(reverse_lazy('accounts:login')),
            })
            plain_message = (
                f'Hello {user.get_full_name() or user.username},\n\n'
                f'Your account has been created on the {settings.CHURCH_NAME} management system.\n\n'
                f'Username: {user.username}\n'
                f'Password: {password}\n\n'
                f'Login at: {self.request.build_absolute_uri(reverse_lazy("accounts:login"))}\n\n'
                f'Please change your password after your first login.\n\n'
                f'God bless you,\n{settings.CHURCH_NAME}'
            )
            send_mail(
                subject,
                plain_message,
                settings.CHURCH_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception:
            pass


class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20


class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


class RolePermissionView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = 'accounts/role_permissions.html'

    def get(self, request):
        context = self.build_context()
        return render(request, self.template_name, context)

    def post(self, request):
        for role, _label in User.ROLE_CHOICES:
            selected = request.POST.getlist(f'modules_{role}')
            RoleModulePermission.objects.filter(role=role).delete()
            if selected:
                RoleModulePermission.objects.bulk_create([
                    RoleModulePermission(role=role, module=module) for module in selected
                ])
        messages.success(request, 'Role permissions updated successfully.')
        return redirect('accounts:permissions')

    def build_context(self):
        existing = {}
        for perm in RoleModulePermission.objects.all():
            existing.setdefault(perm.role, set()).add(perm.module)
        return {
            'modules': MODULES,
            'roles': User.ROLE_CHOICES,
            'existing': existing,
        }
