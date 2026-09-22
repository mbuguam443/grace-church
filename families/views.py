from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView
from members.models import Family
from .models import FamilyRelationship


class FamilyDetailView(LoginRequiredMixin, DetailView):
    model = Family
    template_name = 'families/family_detail.html'
    context_object_name = 'family'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members = self.object.familyrelationship_set.select_related('member').all()
        context['fathers'] = members.filter(relationship='father')
        context['mothers'] = members.filter(relationship='mother')
        context['spouses'] = members.filter(relationship='spouse')
        context['children'] = members.filter(relationship='child')
        context['others'] = members.filter(relationship='other')
        context['page_title'] = f'Family: {self.object.name}'
        return context


class AddMemberToFamilyView(LoginRequiredMixin, CreateView):
    model = FamilyRelationship
    fields = ['member', 'relationship']
    template_name = 'families/add_member.html'

    def dispatch(self, request, *args, **kwargs):
        self.family = Family.objects.get(pk=self.kwargs['family_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['family'] = self.family
        context['page_title'] = f'Add Member to {self.family.name}'
        return context

    def form_valid(self, form):
        form.instance.family = self.family
        response = super().form_valid(form)
        messages.success(self.request, 'Member added to family successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('families:family_detail', kwargs={'pk': self.family.pk})


class RemoveMemberFromFamilyView(LoginRequiredMixin, DeleteView):
    model = FamilyRelationship
    template_name = 'families/confirm_remove.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Remove Member from Family'
        return context

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Member removed from family successfully.')
        return response

    def get_success_url(self):
        return reverse_lazy('families:family_detail', kwargs={'pk': self.object.family.pk})
