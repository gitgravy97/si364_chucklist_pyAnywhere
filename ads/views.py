from django.shortcuts import render
from django.views import View
from django.conf import settings

"""
# Create your views here.
class HomeView(View):
    def get(self, request) :
        cleanup()
        print(request.get_host())
        host = request.get_host()
        islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
        context = {
            'installed' : settings.INSTALLED_APPS,
            'islocal' : islocal
        }
        return render(request, 'main_home.html', context)

# Remove ads > 30 minutes old
from ads.models import Ad
from datetime import timedelta
from django.utils import timezone

# https://stackoverflow.com/questions/37607411/django-runtimewarning-datetimefield-received-a-naive-datetime-while-time-zon/37607525
def cleanup() :
    time_threshold = timezone.now() - timedelta(minutes=30)
    count = Ad.objects.filter(created_at__lt=time_threshold).count()
    if count > 0 :
        Ad.objects.filter(created_at__lt=time_threshold).delete()
        print('Deleted',count,' expired ads')
"""

from ads.models import Ad

from django.views import View
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from ads.util import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from ads.forms import CreateForm

class AdListView(OwnerListView):
    model = Ad
    template_name = "ad_list.html"

class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ad_detail.html"

class AdCreateView(OwnerCreateView):
    model = Ad
    fields = ['title', 'price', 'text']
    template_name = "ad_form.html"

class AdUpdateView(OwnerUpdateView):
    model = Ad
    fields = ['title', 'price', 'text']
    template_name = "ad_form.html"

class AdDeleteView(OwnerDeleteView):
    model = Ad
    template_name = "ad_delete.html"

class AdFormView(LoginRequiredMixin, View):
    template = 'ads/form.html'
    success_url = reverse_lazy('ads')
    def get(self, request, pk=None) :
        if not pk : 
            form = CreateForm()
        else: 
            ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
            form = CreateForm(instance=ad)
        ctx = { 'form': form }
        return render(request, self.template, ctx)

    def post(self, request, pk=None) :
        if not pk:
            form = CreateForm(request.POST, request.FILES or None)
        else:
            ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
            form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template, ctx)

        # Adjust the model owner before saving
        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        print("!")
        return redirect(self.success_url)

def stream_file(request, pk) :
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.content_type
    response['Content-Length'] = len(ad.picture)
    response.write(ad.picture)
    return response