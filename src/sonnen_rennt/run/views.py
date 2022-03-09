from datetime import date, datetime, time, timedelta

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, Http404
from django.views.generic import ListView, DetailView, View, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from .forms import RunCreateEditForm, RunEditForm
from .models import Run

from group.score_updater import score_update

# TODO login required / owner of run or superuser

ERROR_RUN_NOT_EXISTING_FORWARD_LIST = "Dieser Lauf existiert nicht! Wir haben Sie deshalb zu Ihrer Laufliste weitergeleitet!"
ERROR_RUN_NOT_EXISTING_FORWARD_CREATE = "Dieser Lauf existiert nicht! Hier können Sie einen neuen anlegen!"
ERROR_NO_ACCESS_TO_RUN = "Sie haben auf diesen Lauf keinen Zugriff! Wir haben Sie deshalb zu Ihrer Laufliste weitergeleitet!"


def dashboard_forward(request, *args, **kargs):
    return redirect("/run/dashboard/")


def dashboard_view(request, *args, **kargs):
    return render(request, "root.html", {})


class RunDetailView(View):

    def get(self, request, *args, **kwargs):
        run_id = kwargs.get('run_id')

        exists = Run.objects.filter(id=run_id).exists()
        if not exists:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_LIST)
            return redirect("/run/list-user/")

        run = Run.objects.get(id=run_id)

        if run is None:
            raise Http404(ERROR_RUN_NOT_EXISTING_FORWARD_LIST)

        # ACCESS CONTROL ##############
        if not run.group:  # runs for groups are public by design
            if run.creator.user.id != request.user.id:
                messages.error(request, ERROR_NO_ACCESS_TO_RUN)
                return redirect("/run/list-user/")
        ###############################

        context = {
            'run': run,
            # 'run_details_view': True
        }

        return render(request, "run/run_detail.html", context)

    # def get_object(self):
    #     run_id = self.kwargs.get('run_id')
    #     return get_object_or_404(Run, id=run_id)


# TODO: minimal start_date one week before (in create and update)
class RunCreateView(View):
    template_name = 'run/run_create.html'

    def get(self, request, *args, **kwargs):
        form = RunCreateEditForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RunCreateEditForm(request.POST)
        if form.is_valid() and request.user:
            run = form.create_new(request.user)
            if run:
                score_update()
                return redirect("/run/detail/" + str(run.id))
            else:
                form = RunCreateEditForm()
        return render(request, self.template_name, {'form': form})


class RunUpdateView(View):
    template_name = "run/run_update.html"

    def get(self, request, *args, **kwargs):
        run_id = kwargs.get('run_id')

        ################################
        exists = Run.objects.filter(id=run_id).exists()
        if not exists:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/run/create/")

        run = Run.objects.get(id=run_id)

        if run is None:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/run/create/")

        # ACCESS CONTROL ##############
        if run.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_RUN)
            return redirect("/run/list-user/")
        ###############################

        init = {
            'route': run.route,
            'distance': run.distance,
            'elevation_gain': run.elevation_gain,
            'time_start': run.time_start,
            'duration': run.duration,
            'group': run.group,
            'type': run.type,
            'note': run.note,
        }
        form = RunEditForm(initial=init)

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RunEditForm(request.POST)
        run_id = kwargs.get('run_id')

        ################################
        exists = Run.objects.filter(id=run_id).exists()
        if not exists:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/run/create/")

        run = Run.objects.get(id=run_id)

        if run is None:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/run/create/")

        # ACCESS CONTROL ##############
        if run.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_RUN)
            return redirect("/run/list-user/")
        ###############################

        if form.is_valid() and request.user:
            run = form.save_existing(request.user, run)
            if run:
                score_update()
                return redirect("/run/detail/" + str(run.id))
            else:
                form = RunEditForm()
        return render(request, self.template_name, {'form': form})


# TODO run delete buttons

# TODO owner check
class RunDeleteView(View):
    template_name = 'run/run_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        run_id = kwargs.get('run_id')

        ################################
        exists = Run.objects.filter(id=run_id).exists()
        if not exists:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/run/create/")

        run = Run.objects.get(id=run_id)

        if run is None:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/run/create/")

        # ACCESS CONTROL ##############
        if run.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_RUN)
            return redirect("/run/list-user/")
        ###############################

        context = {
            'run': run
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = RunCreateEditForm(request.POST)
        run_id = kwargs.get('run_id')

        ################################
        exists = Run.objects.filter(id=run_id).exists()
        if not exists:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_LIST)
            return redirect("/run/create/")

        run = Run.objects.get(id=run_id)

        if run is None:
            messages.error(request, ERROR_RUN_NOT_EXISTING_FORWARD_LIST)
            return redirect("/run/create/")

        # ACCESS CONTROL ##############
        if run.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_RUN)
            return redirect("/run/list-user/")
        ###############################

        run.delete()
        score_update()
        messages.success(request, "Lauf erfolgreich gelöscht!")

        return redirect("/run/list-user/")


# class RunListView(ListView):
#     queryset = Run.objects.all()


# @login_required
# def list_group_view(request, *args, **kargs):
#     return HttpResponse("<h1>list_group_view</h1>")


class RunListUserView(View):
    template_name = 'run/run_list_user.html'

    def get(self, request, *args, **kwargs):
        queryset = Run.objects.filter(creator=request.user.profile.id).order_by("-time_start")
        paginator = Paginator(queryset, 10)
        page = request.GET.get('page')

        context = {
            'page_obj': paginator.page(page or 1)
        }

        return render(request, self.template_name, context)
