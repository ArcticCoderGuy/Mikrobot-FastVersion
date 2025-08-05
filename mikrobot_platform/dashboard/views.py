from django.shortcuts import render
from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'MIKROBOT Trading Dashboard'
        return context


def dashboard_view(request):
    """Simple dashboard view function"""
    return render(request, 'dashboard/index.html', {
        'title': 'MIKROBOT Trading Dashboard',
    })