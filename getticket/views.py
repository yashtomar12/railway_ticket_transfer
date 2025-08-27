from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import UserRegisterForm, TicketTransferForm, StaffLoginForm
from .models import TicketTransferRequest, RailwayStaff
from django.contrib import messages

import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from openai import OpenAI

# Configure Gemini
genai.configure(api_key=getattr(settings, "GEMINI_API_KEY", None))

# Instantiate OpenAI client if API key available
_OPENAI_KEY = getattr(settings, "OPENAI_API_KEY", None)
client = OpenAI(api_key=_OPENAI_KEY) if _OPENAI_KEY else None

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(user_message)

            return JsonResponse({"reply": response.text})
        except Exception as e:
            return JsonResponse({"reply": f"⚠️ Error: {str(e)}"})

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        # accept JSON body or form data
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        user_message = data.get("message", "")

        if not getattr(settings, "GEMINI_API_KEY", None):
            return JsonResponse({"reply": "Gemini API key not configured on server."}, status=500)

        try:
            # Use Gemini generative model to produce a reply
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(user_message)

            # response may contain `.text` or `.content`; handle common shapes
            reply_text = getattr(response, "text", None) or getattr(response, "content", None)
            if not reply_text:
                # try nested structure
                reply_text = str(response)

            return JsonResponse({"reply": reply_text})
        except Exception as e:
            return JsonResponse({"reply": f"⚠️ Gemini error: {str(e)}"}, status=500)
    return JsonResponse({"reply": "Invalid request"})


# ----- User Login -----
class CustomLoginView(LoginView):
    template_name = "getticket/login.html"
    redirect_authenticated_user = True
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        if user and not user.is_staff:  # ✅ only normal users
            login(self.request, user)
            return redirect("getticket:user_dashboard")
        else:
            messages.error(self.request, "Invalid ID or Password")
            return redirect("getticket:login")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid ID or Password")
        return redirect("getticket:login")


# ----- Staff Login -----
class StaffLoginView(LoginView):
    template_name = "getticket/staff_login.html"
    redirect_authenticated_user = True
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        if user and user.is_staff:  # ✅ only staff accounts
            login(self.request, user)
            return redirect("getticket:staff_dashboard")
        else:
            messages.error(self.request, "Invalid Staff ID or Password")
            return redirect("getticket:staff_login")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid Staff ID or Password")
        return redirect("getticket:staff_login")



# ---------------------------
# LANDING & HOME
# ---------------------------
def landing_page(request):
    return render(request, "getticket/landing.html")

def home(request):
    return render(request, "getticket/home.html")


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # save new user
            login(request, user)  # auto login after registration
            return redirect("getticket:request_transfer")  # go to transfer page
        else:
            print(form.errors)  # 👈 debug in console
    else:
        form = UserRegisterForm()
    
    return render(request, "getticket/register.html", {"form": form})

# ---------------------------
# USER LOGIN (normal users only)
# ---------------------------
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # 🚫 Prevent staff login here
            if hasattr(user, "railwaystaff"):
                return render(request, "getticket/login.html", {
                    "form": form,
                    "error": "❌ Staff must log in from the Staff Login page."
                })

            # ✅ Normal user login
            login(request, user)
            return redirect("getticket:user_dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "getticket/login.html", {"form": form})


# ---------------------------
# USER DASHBOARD
# ---------------------------
@login_required
def user_dashboard(request):
    return render(request, "getticket/user_dashboard.html")


# ---------------------------
# REQUEST TRANSFER (user)
# ---------------------------
@login_required
def request_transfer(request):
    if request.method == "POST":
        form = TicketTransferForm(request.POST, request.FILES)
        if form.is_valid():
            ticket_request = form.save(commit=False)
            ticket_request.user = request.user
            ticket_request.save()
            return redirect("getticket:my_requests")
    else:
        form = TicketTransferForm()
    return render(request, "getticket/request_transfer.html", {"form": form})

# ---------------------------
# LOGOUT VIEW
# ---------------------------
def logout_view(request):
    logout(request)
    return redirect("getticket:home")   # after logout, go to landing/home page


# ---------------------------
# MY REQUESTS (user)
# ---------------------------
@login_required
def my_requests(request):
    requests = TicketTransferRequest.objects.filter(user=request.user)
    return render(request, "getticket/my_requests.html", {"requests": requests})


# ---------------------------
# STAFF LOGIN (dedicated page)
# ---------------------------
def staff_login(request):
    if request.method == "POST":
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            staff_user = form.cleaned_data["user"]
            login(request, staff_user)
            return redirect("getticket:staff_dashboard")
    else:
        form = StaffLoginForm()
    return render(request, "getticket/staff_login.html", {"form": form})


# ---------------------------
# STAFF DASHBOARD
# ---------------------------
@login_required
def staff_dashboard(request):
    if not hasattr(request.user, "railwaystaff"):
        return redirect("getticket:home")
    requests = TicketTransferRequest.objects.all().order_by("-created_at")
    return render(request, "getticket/staff_dashboard.html", {"requests": requests})


# ---------------------------
# STAFF ACTIONS
# ---------------------------
@require_POST
@login_required
def approve_request(request, pk):
    ticket_request = get_object_or_404(TicketTransferRequest, pk=pk)
    ticket_request.status = "APPROVED"
    ticket_request.remark = request.POST.get("remark", "Approved by staff")  # ✅ FIX
    ticket_request.save()
    return redirect("getticket:staff_dashboard")


@login_required
def reject_request(request, pk):
    ticket_request = get_object_or_404(TicketTransferRequest, pk=pk)

    if request.method == "POST":
        remark = request.POST.get("remark", "Rejected by staff")  # ✅ FIX
        ticket_request.status = "REJECTED"
        ticket_request.remark = remark  # ✅ FIX
        ticket_request.save()
        return redirect("getticket:staff_dashboard")

    # Show remark form
    return render(request, "getticket/reject_request.html", {"request_obj": ticket_request})
