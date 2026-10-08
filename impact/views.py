from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.views import ContentWriteMixin
from core.models import ChurchSetting

from .forms import FundedPersonForm
from .models import ChurchPlant, FundedPerson, impact_counts

IMPACT_FIELDS = [
    'impact_1_value', 'impact_1_label', 'impact_1_note',
    'impact_2_value', 'impact_2_label', 'impact_2_note',
    'impact_3_value', 'impact_3_label', 'impact_3_note',
]


class ImpactStatsView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    """The dashboard control for the public 'Your Impact' section."""

    model = ChurchSetting
    fields = IMPACT_FIELDS
    template_name = 'impact/stats.html'
    success_url = reverse_lazy('impact:stats')

    def get_object(self, queryset=None):
        return ChurchSetting.get_settings()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        counts = impact_counts()
        context['live_counts'] = [
            {'label': 'Families Fed', 'count': counts['families_fed'],
             'source': 'Food & Family Support records', 'url': reverse('impact:funded-list') + '?category=food'},
            {'label': 'Students Sponsored', 'count': counts['students_sponsored'],
             'source': 'School Fees & Scholarship records', 'url': reverse('impact:funded-list') + '?category=scholarship'},
            {'label': 'Churches Planted', 'count': counts['churches_planted'],
             'source': 'Planted / Active church records', 'url': reverse('impact:churchplant-list')},
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, 'The "Your Impact" section has been updated.')
        return super().form_valid(form)


class FundedPersonListView(LoginRequiredMixin, ListView):
    model = FundedPerson
    template_name = 'impact/funded_list.html'
    context_object_name = 'people'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '').strip()
        status = self.request.GET.get('status', '').strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(record_number__icontains=search)
                | Q(note__icontains=search)
                | Q(story__icontains=search)
                | Q(location__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(assigned_deacon__first_name__icontains=search)
                | Q(assigned_deacon__last_name__icontains=search)
            )
        if category:
            queryset = queryset.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['category_choices'] = FundedPerson.CATEGORY_CHOICES
        context['status_choices'] = FundedPerson.STATUS_CHOICES
        context['total_count'] = FundedPerson.objects.count()
        context['public_count'] = FundedPerson.objects.filter(is_public=True).count()
        context['category_cards'] = [
            {'label': label, 'count': FundedPerson.objects.filter(category=key).count()}
            for key, label in FundedPerson.CATEGORY_CHOICES
        ]
        return context


class FundedPersonCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = FundedPerson
    form_class = FundedPersonForm
    template_name = 'impact/funded_form.html'
    success_url = reverse_lazy('impact:funded-list')

    def form_valid(self, form):
        messages.success(self.request, 'Person funded recorded successfully.')
        return super().form_valid(form)


class FundedPersonUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = FundedPerson
    form_class = FundedPersonForm
    template_name = 'impact/funded_form.html'
    success_url = reverse_lazy('impact:funded-list')

    def form_valid(self, form):
        messages.success(self.request, 'Record updated successfully.')
        return super().form_valid(form)


class FundedPersonTogglePublicView(LoginRequiredMixin, ContentWriteMixin, View):
    """Approve / unapprove a record for the public Give page."""

    def post(self, request, pk):
        person = get_object_or_404(FundedPerson, pk=pk)
        person.is_public = not person.is_public
        person.save(update_fields=['is_public', 'updated_at'])
        if person.is_public:
            messages.success(request, f'"{person.name}" is now shown on the public Give page.')
        else:
            messages.success(request, f'"{person.name}" is no longer shown publicly.')
        return redirect('impact:funded-list')


class FundedPersonDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = FundedPerson
    template_name = 'impact/funded_confirm_delete.html'
    context_object_name = 'person'
    success_url = reverse_lazy('impact:funded-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Record deleted.')
        return super().delete(request, *args, **kwargs)


class ChurchPlantListView(LoginRequiredMixin, ListView):
    model = ChurchPlant
    template_name = 'impact/churchplant_list.html'
    context_object_name = 'plants'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(location__icontains=search)
                | Q(pastor__icontains=search)
                | Q(note__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = ChurchPlant.STATUS_CHOICES
        context['total_count'] = ChurchPlant.objects.count()
        context['status_cards'] = [
            {'label': label, 'count': ChurchPlant.objects.filter(status=key).count()}
            for key, label in ChurchPlant.STATUS_CHOICES
        ]
        return context


class ChurchPlantCreateView(LoginRequiredMixin, ContentWriteMixin, CreateView):
    model = ChurchPlant
    template_name = 'impact/churchplant_form.html'
    fields = ['name', 'location', 'pastor', 'date_planted', 'status', 'note']
    success_url = reverse_lazy('impact:churchplant-list')

    def form_valid(self, form):
        messages.success(self.request, 'Church plant recorded successfully.')
        return super().form_valid(form)


class ChurchPlantUpdateView(LoginRequiredMixin, ContentWriteMixin, UpdateView):
    model = ChurchPlant
    template_name = 'impact/churchplant_form.html'
    fields = ['name', 'location', 'pastor', 'date_planted', 'status', 'note']
    success_url = reverse_lazy('impact:churchplant-list')

    def form_valid(self, form):
        messages.success(self.request, 'Church plant updated successfully.')
        return super().form_valid(form)


class ChurchPlantDeleteView(LoginRequiredMixin, ContentWriteMixin, DeleteView):
    model = ChurchPlant
    template_name = 'impact/churchplant_confirm_delete.html'
    context_object_name = 'plant'
    success_url = reverse_lazy('impact:churchplant-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Church plant deleted.')
        return super().delete(request, *args, **kwargs)
