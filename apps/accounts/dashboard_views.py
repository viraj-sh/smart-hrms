
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


@login_required
def admin_dashboard(request):
    if request.user.role != "Admin":
        raise PermissionDenied
    return render(request, "accounts/admin_dashboard.html")


@login_required
def hr_dashboard(request):
    if request.user.role != "HR":
        raise PermissionDenied
    return render(request, "accounts/hr_dashboard.html")


@login_required
def employee_dashboard(request):
    if request.user.role != "Employee":
        raise PermissionDenied
    return render(request, "accounts/employee_dashboard.html")
