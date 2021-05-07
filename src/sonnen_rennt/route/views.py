from datetime import date, datetime, time, timedelta

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, Http404
from django.views.generic import ListView, DetailView, View, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from .forms import RouteCreateForm
from .models import Route

# TODO login required / owner of run or superuser

ERROR_ROUTE_NOT_EXISTING_FORWARD_LIST = "Diese Route existiert nicht! Wir haben Sie deshalb zu Ihrer Routenliste weitergeleitet!"
ERROR_ROUTE_NOT_EXISTING_FORWARD_CREATE = "Diese Route existiert nicht! Hier können Sie eine neue anlegen!"
ERROR_NO_ACCESS_TO_ROUTE = "Sie haben auf diese Route keinen Zugriff! Wir haben Sie deshalb zu Ihrer Laufliste weitergeleitet!"


def dashboard_forward(request, *args, **kargs):
    return redirect("/route/dashboard/")


def dashboard_view(request, *args, **kargs):
    return render(request, "root.html", {})


def help(request):
    return render(request, "route/help.html", {})


# TODO owner check
class RouteDetailView(DetailView):

    def get(self, request, *args, **kwargs):
        route_id = kwargs.get('route_id')

        exists = Route.objects.filter(id=route_id).exists()
        if not exists:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_LIST)
            return redirect("/route/list-user/")

        route = Route.objects.get(id=route_id)

        if route is None:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_LIST)
            return redirect("/route/list-user/")

        # ACCESS CONTROL ##############
        # if route.creator.user != request.user.id:
        # Routes are public by design
        ###############################

        context = {
            'route': route,
            # 'route_details_view': True
        }

        return render(request, "route/route_detail.html", context)

# TODO modify save method
class RouteCreateView(View):
    template_name = 'route/route_create.html'

    def get(self, request, *args, **kwargs):
        form = RouteCreateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RouteCreateForm(request.POST)
        if form.is_valid() and request.user:
            route = form.create_new(request.user)
            if route:
                return redirect("/route/detail/" + str(route.id))
            else:
                form = RouteCreateForm()
        return render(request, self.template_name, {'form': form})


# TODO test
class RouteUpdateView(UpdateView):
    template_name = "route/route_update.html"

    def get(self, request, *args, **kwargs):
        route_id = kwargs.get('route_id')

        ################################
        exists = Route.objects.filter(id=route_id).exists()
        if not exists:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/route/create/")

        route = Route.objects.get(id=route_id)

        if route is None:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/route/create/")

        # ACCESS CONTROL ##############
        if route.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_ROUTE)
            return redirect("/route/list-user/")
        ###############################

        init = {
            'title': route.title,
            'distance': route.distance,
            'elevation_gain': route.elevation_gain,
            'description': route.description,
            'link': route.link,
        }
        form = RouteCreateForm(initial=init)

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RouteCreateForm(request.POST)
        route_id = kwargs.get('route_id')

        ################################
        exists = Route.objects.filter(id=route_id).exists()
        if not exists:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/route/create/")

        route = Route.objects.get(id=route_id)

        if route is None:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/route/create/")

        # ACCESS CONTROL ##############
        if route.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_ROUTE)
            return redirect("/route/list-user/")
        ###############################

        if form.is_valid() and request.user:
            route = form.save_existing(request.user, route)
            if route:
                return redirect("/route/detail/" + str(route.id))
            else:
                form = RouteCreateForm()
        return render(request, self.template_name, {'form': form})


class RouteDeleteView(View):
    template_name = 'route/route_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        route_id = kwargs.get('route_id')

        ################################
        exists = Route.objects.filter(id=route_id).exists()
        if not exists:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/route/create/")

        route = Route.objects.get(id=route_id)

        if route is None:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_CREATE)
            return redirect("/route/create/")

        # ACCESS CONTROL ##############
        if route.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_ROUTE)
            return redirect("/route/list-user/")
        ###############################

        context = {
            'route': route
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = RouteCreateForm(request.POST)
        route_id = kwargs.get('route_id')

        ################################
        exists = Route.objects.filter(id=route_id).exists()
        if not exists:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_LIST)
            return redirect("/route/create/")

        route = Route.objects.get(id=route_id)

        if route is None:
            messages.error(request, ERROR_ROUTE_NOT_EXISTING_FORWARD_LIST)
            return redirect("/route/create/")

        # ACCESS CONTROL ##############
        if route.creator.user.id != request.user.id:
            messages.error(request, ERROR_NO_ACCESS_TO_ROUTE)
            return redirect("/route/list-user/")
        ###############################

        route.delete()
        messages.success(request, "Gruppe erfolgreich gelöscht!")

        return redirect("/route/list-user/")


class RouteListView(View):
    template_name = "route/route_list.html"

    def get(self, request, *args, **kwargs):
        queryset = Route.objects.all()
        paginator = Paginator(queryset, 10)
        page = request.GET.get('page')

        context = {
            'page_obj': paginator.page(page or 1)
        }

        return render(request, self.template_name, context)


# @login_required
# def list_group_view(request, *args, **kargs):
#     return HttpResponse("<h1>list_group_view</h1>")


class RouteListUserView(View):
    template_name = 'route/route_list.html'

    def get(self, request, *args, **kwargs):
        queryset = Route.objects.filter(creator=request.user.profile.id)
        paginator = Paginator(queryset, 10)
        page = request.GET.get('page')

        context = {
            'page_obj': paginator.page(page or 1)
        }

        return render(request, self.template_name, context)

