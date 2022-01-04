import functools
from datetime import datetime
import logging

from django.contrib.admin import helpers
from django.template.response import TemplateResponse

log = logging.getLogger(__name__)


def duration_log():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self):
            start = datetime.utcnow()
            result = func(self)
            end = datetime.utcnow()
            log.info(f'Duration {func.__name__}: {end - start}')
            return result

        return wrapper
    return decorator


def action_form(form_class=None, initial_value="Change reason"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):

            if 'confirm' in request.POST and request.POST:
                form = form_class(request.POST)
                if form.is_valid():
                    func(self, request, queryset, form)
                    self.message_user(request, 'Action performed')
                    return None

            form = form_class(initial={'comment': initial_value})
            context = dict(
                self.admin_site.each_context(request),
                title=form_class.title,
                action=func.__name__,
                opts=self.model._meta,
                queryset=queryset, form=form,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME)

            return TemplateResponse(request, 'admin/form_action_confirmation.html', context)

        wrapper.short_description = form_class.title

        return wrapper

    return decorator


def device_event_form(form_class=None, initial_value="Event type"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):

            if 'confirm' in request.POST and request.POST:
                form = form_class(request.POST)
                if form.is_valid():
                    func(self, request, queryset, form)
                    event_type = request.POST.get('event', '')
                    self.message_user(request, f'Event {event_type} sent to device(s)')
                    return None

            form = form_class(initial={'event': initial_value})
            context = dict(
                self.admin_site.each_context(request),
                title=form_class.title,
                action=func.__name__,
                opts=self.model._meta,
                queryset=queryset, form=form,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME)

            return TemplateResponse(request, 'admin/device_send_event.html', context)

        wrapper.short_description = form_class.title

        return wrapper

    return decorator
