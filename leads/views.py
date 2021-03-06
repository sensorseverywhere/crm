from nis import cat
from unicodedata import category
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.views import generic
from .forms import LeadForm, LeadModelForm, LeadCategoryUpdateForm, CustomUserCreationForm, AssignAgentForm
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Lead, Agent, Category

class SignupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/lead_list.html'
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            qs = Lead.objects.filter(organisation=user.userprofile, agent__isnull=False)
        else:
            qs = Lead.objects.filter(agent__user=self.request.user, agent__isnull=False)
            # filter for the agent that is logged in
            qs = qs.filter(agent__user=user)
        return qs

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organisor:
            qs = Lead.objects.filter(organisation=user.userprofile, agent__isnull=True)

            context.update({
                "unassigned_leads": qs
            })
        return context

def lead_list(request):
    leads = Lead.objects.all()
    context = { 
        "leads": leads
    }
    return render(request, 'leads/lead_list.html', context)


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            qs = Lead.objects.filter(organisation=user.userprofile)
        else:
            qs = Lead.objects.filter(agent__user=self.request.user)
            # filter for the agent that is logged in
            qs = qs.filter(agent__user=user)
        return qs


# def lead_detail(request, pk):
#     lead = Lead.objects.get(id=pk)
#     return render(request, "leads/lead_detail.html", {"lead": lead})


class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm
    
    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        # TODO send email
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test@test.com"]
        )
        return super(LeadCreateView, self).form_valid(form)


def lead_create(request):
    form = LeadModelForm()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form
    }
        
    return render(request, "leads/lead_create.html", context)


class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        qs = Lead.objects.filter(organisation=user.userprofile)

        return qs
    
    def get_success_url(self):
        return reverse("leads:lead-list")


def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == 'POST':
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form,
        "lead": lead
    }
    return render(request, "leads/lead_update.html", context)


class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"

    def get_queryset(self):
        user = self.request.user
        qs = Lead.objects.filter(organisation=user.userprofile)

        return qs

    def get_success_url(self):
        return reverse("leads:lead-list")


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")


class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update ({
            "request": self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class LandingPageView(generic.TemplateView):
    template_name = 'landing.html'

    

def landing_page(request):
    return render(request, "landing.html")


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(user.agent.organsation)
        
        context.update({
            "unassigned_lead_count": Lead.objects.filter(category__isnull=True).count()
        })
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            qs = Category.objects.filter(organisation=user.userprofile)
        else:
            qs = Category.objects.filter(user.agent.organsation)
        return qs


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    # def get_context_data(self, **kwargs):
    #     context = super(CategoryDetailView, self).get_context_data(**kwargs)

    #     #queryset = Lead.objects.filter(category=self.get_object())
    #     # replaces above qs due to 'related_name' attribute on model
    #     leads = self.get_object().leads.all()

    #     context.update({
    #         "leads": leads
    #     })
    #     return context


    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(user.agent.organsation)
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            qs = Lead.objects.filter(organisation=user.userprofile)
        else:
            qs = Lead.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            qs = qs.filter(agent__user=user)
        return qs
    
    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk":self.get_object().id})


# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == 'POST':
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             lead.first_name = first_name
#             lead.last_name = last_name
#             lead.age = age
#             lead.save()
#             return redirect('/leads')
#     context = {
#         'form': form
#     }
#     return render(request, 'leads/lead_update.html', context)
        

# def lead_create(request):
#     if request.method == 'POST':
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             print(form.cleaned_data)
#             first_name = form.cleaned_data["first_name"]
#             last_name = form.cleaned_data["last_name"]
#             age = form.cleaned_data["age"]
#             agent = Agent.objects.first()
#             Lead.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 age=age,
#                 agent=agent
#             )
#     context = {
#         "form": form
#     }
        
#     return render(request, "leads/lead_create.html", context)