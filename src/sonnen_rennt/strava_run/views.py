from django.http import Http404
from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from django.contrib import messages

from run.models import StravaRun

ERROR_RUN_NOT_EXISTING_FORWARD_LIST = "Dieser Lauf existiert nicht! Wir haben Sie deshalb zur Strava Laufliste weitergeleitet!"


def forward(request):
    return redirect("https://www.strava.com/clubs/849711/")


class StravaRunDetailView(View):

    def get(self, request, *args, **kwargs):
        run_id = kwargs.get('run_id')

        exists = StravaRun.objects.filter(id=run_id).exists()
        if not exists:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_LIST)
            return redirect("/strava-run/list-user/")

        run = StravaRun.objects.get(id=run_id)

        if run is None:
            raise Http404(ERROR_RUN_NOT_EXISTING_FORWARD_LIST)

        context = {
            'run': run,
        }

        return render(request, "run/strava_run_detail.html", context)


class StravaRunListView(View):
    template_name = 'run/strava_run_list.html'

    def get(self, request, *args, **kwargs):
        queryset = StravaRun.objects.all()
        paginator = Paginator(queryset, 10)
        page = request.GET.get('page')

        tab = request.GET.get('tab')
        if tab is None:
            tab = 'runs'

        context = {
            'page_obj': paginator.page(page or 1),
            'tab': tab
        }

        context.update({})

        return render(request, self.template_name, context)
