from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, DetailView
from accounts.views import ContentWriteMixin
from .models import Attendance
from services.models import Service


class AttendanceForm(ModelForm):
    class Meta:
        model = Attendance
        fields = ['service', 'member', 'attendance_type', 'visitor_name', 'notes']


class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        service_id = self.request.GET.get('service', '')
        date = self.request.GET.get('date', '')

        if service_id:
            queryset = queryset.filter(service_id=service_id)
        if date:
            queryset = queryset.filter(service__date=date)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        context['service_filter'] = self.request.GET.get('service', '')
        context['date_filter'] = self.request.GET.get('date', '')
        return context


class AttendanceCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = Attendance
    template_name = 'attendance/attendance_form.html'
    fields = ['service', 'member', 'attendance_type', 'visitor_name', 'notes']
    success_url = reverse_lazy('attendance:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, 'Attendance record created successfully.')
        return super().form_valid(form)


class AttendanceByServiceView(LoginRequiredMixin, DetailView):
    model = Service
    template_name = 'attendance/attendance_by_service.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendances'] = self.object.attendances.all()
        context['attendance_form'] = AttendanceForm(initial={'service': self.object})
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, 'Attendee added successfully.')
            return redirect('attendance:by_service', pk=self.object.pk)
        context = self.get_context_data(object=self.object)
        context['attendance_form'] = form
        return self.render_to_response(context)


class AttendanceDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = Attendance
    template_name = 'attendance/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:attendance_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Attendance record deleted successfully.')
        return super().delete(request, *args, **kwargs)
