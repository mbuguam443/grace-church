from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from accounts.views import ContentWriteMixin
from .models import Child, ChildAttendance


class ChildListView(LoginRequiredMixin, ListView):
    model = Child
    template_name = 'children/child_list.html'
    context_object_name = 'children'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        school_class = self.request.GET.get('school_class', '')
        if search:
            queryset = queryset.filter(first_name__icontains=search) | queryset.filter(last_name__icontains=search)
        if school_class:
            queryset = queryset.filter(school_class__iexact=school_class)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['school_class'] = self.request.GET.get('school_class', '')
        context['classes'] = Child.objects.values_list('school_class', flat=True).distinct()
        return context


class ChildCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Child
    template_name = 'children/child_form.html'
    fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'parent', 'school_class', 'teacher', 'allergies', 'emergency_contact', 'photo', 'is_active']
    success_url = reverse_lazy('children:child_list')

    def form_valid(self, form):
        messages.success(self.request, 'Child registered successfully.')
        return super().form_valid(form)


class ChildUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = Child
    template_name = 'children/child_form.html'
    fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'parent', 'school_class', 'teacher', 'allergies', 'emergency_contact', 'photo', 'is_active']
    success_url = reverse_lazy('children:child_list')

    def form_valid(self, form):
        messages.success(self.request, 'Child updated successfully.')
        return super().form_valid(form)


class ChildDetailView(LoginRequiredMixin, DetailView):
    model = Child
    template_name = 'children/child_detail.html'
    context_object_name = 'child'


class ChildDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Child
    template_name = 'children/child_confirm_delete.html'
    success_url = reverse_lazy('children:child_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Child record deleted successfully.')
        return super().delete(request, *args, **kwargs)


class ChildCheckinView(LoginRequiredMixin, View):
    def post(self, request, pk):
        child = get_object_or_404(Child, pk=pk)
        today = timezone.localdate()
        attendance, created = ChildAttendance.objects.get_or_create(
            child=child,
            date=today,
            defaults={
                'checked_in': True,
                'checkin_time': timezone.localtime().time(),
                'checked_in_by': request.user,
            }
        )
        if not created:
            if attendance.checked_in:
                messages.warning(request, f'{child} is already checked in.')
            else:
                attendance.checked_in = True
                attendance.checkin_time = timezone.localtime().time()
                attendance.checked_in_by = request.user
                attendance.save()
                messages.success(request, f'{child} checked in successfully.')
        else:
            messages.success(request, f'{child} checked in successfully.')
        return redirect('children:child_list')


class ChildCheckoutView(LoginRequiredMixin, View):
    def post(self, request, pk):
        child = get_object_or_404(Child, pk=pk)
        today = timezone.localdate()
        attendance = ChildAttendance.objects.filter(child=child, date=today).first()
        if attendance:
            if attendance.checked_out:
                messages.warning(request, f'{child} is already checked out.')
            else:
                attendance.checked_out = True
                attendance.checkout_time = timezone.localtime().time()
                attendance.checked_out_by = request.user
                attendance.save()
                messages.success(request, f'{child} checked out successfully.')
        else:
            ChildAttendance.objects.create(
                child=child,
                date=today,
                checked_out=True,
                checkout_time = timezone.localtime().time(),
                checked_out_by=request.user,
            )
            messages.success(request, f'{child} checked out successfully.')
        return redirect('children:child_list')
