from django.shortcuts import render,redirect,get_object_or_404
from .forms import BunkerForm, LoginForm, RegisterForm
from django.contrib import messages
from .models import Booking, ContactMessage, CustomUser,AddBunker,Mechanic, User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q

def index(request):
    query = request.GET.get('q')

    # Default: show all
    bunkers = AddBunker.objects.all()
    mechanics = Mechanic.objects.all()

    # If search keyword exists
    if query:
        bunkers = AddBunker.objects.filter(
            Q(bunker_name__icontains=query) | Q(location__icontains=query)
        )
        mechanics = Mechanic.objects.filter(
            Q(name__icontains=query) | Q(specialization__icontains=query)
        )

    return render(request, 'Vehicle/index.html', {
        'bunkers': bunkers,
        'mechanics': mechanics,
        'query': query
    })

def register_page(request):
    if request.method == "POST":
        user_type = request.POST.get('user_type')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('Vehicle:register_page')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('Vehicle:register_page')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('Vehicle:register_page')

        user = CustomUser(
            user_type=user_type,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            zip=zip_code,
        )
        user.set_password(password)
        user.save()
        messages.success(request, "Registration successful! Please log in.")
        return redirect('Vehicle:login_page')

    return render(request, 'Vehicle/register_page.html')

def about_page(request):
    return render(request,'Vehicle/about_page.html')

def login_page(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        role = request.POST.get('user_type')

        if not role:
            messages.error(request, "Please select a role.")
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)

            if user:
                if role != user.user_type:
                    messages.error(request, f"You must login as {user.user_type.capitalize()}.")
                    return redirect('Vehicle:login_page')

                login(request, user)

                if role == 'admin':
                    return redirect('Vehicle:admin_dashboard')
                elif role == "owner":
                    return redirect('Vehicle:owner_dashboard')
                elif role == "mechanic":
                    return redirect('Vehicle:service_page')
                else:
                    return redirect('Vehicle:user_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid form input.")
    return render(request,'Vehicle/login_page.html', {'form': form})


def owner_dashboard(request):

    if request.user.user_type != 'owner':
        return  redirect('Vehicle:index')
    
    bunkers = AddBunker.objects.filter(owner = request.user)
    bookings = Booking.objects.filter(bunker__in=bunkers).select_related('bunker', 'user')
    mechanics = Mechanic.objects.all()

    return render(request, 'Vehicle/owner_dashboard.html',{
        'bunkers':bunkers,
        'bookings':bookings,
        'mechanics':mechanics
        })
@login_required
def mark_done(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.bunker.owner != request.user:
        messages.error(request, "You are not allowed to modify this booking.")
        return redirect('Vehicle:owner_dashboard')

    booking.status = 'done'
    booking.save()
    messages.success(request, "Booking marked as done ✅")

    return redirect('Vehicle:owner_dashboard')



def user_dashboard(request):
    bookings = Booking.objects.all()
    return render(request, 'Vehicle/user_dashboard.html',{'bookings':bookings})


def is_admin(user):
    return user.is_authenticated and user.user_type == "admin"
@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    # if not request.user.is_superuser:
    #     return redirect('Vehicle:login_page')

    users = CustomUser.objects.all()
    bunkers = AddBunker.objects.all()
    bookings = Booking.objects.all()
    contact_messages  = ContactMessage.objects.all()

    return render(request, 'Vehicle/admin_dashboard.html', {
        'users': users,
        'bunkers': bunkers,
        'bookings': bookings,
        'contact_messages':contact_messages
    })


def add_bunker(request):
    if request.method == "POST":
        form = BunkerForm(request.POST,request.FILES)
        if form.is_valid():
            bunker = form.save(commit=False)
            bunker.owner = request.user
            bunker.save()
            messages.success(request, "Bunker added successfully!")
            return redirect('Vehicle:owner_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BunkerForm()
    return render(request,'Vehicle/add_bunker.html',{'form':form})

def edit_bunker(request,id):
    bunker = get_object_or_404(AddBunker,id = id)
    if request.method == "POST":
        form = BunkerForm(request.POST,request.FILES, instance = bunker)
        if form.is_valid():
            form.save()
            messages.success(request,"Bunks Updated SuccessFullly")
            return redirect('Vehicle:owner_dashboard')
    else:
        form = BunkerForm(instance=bunker)
    return render(request,'Vehicle/edit_bunker.html',{'form':form,'bunker':bunker})

def delete_bunker(request,id):
    bunker = get_object_or_404(AddBunker,id = id)
    bunker.delete()
    messages.success(request,"Bunk deleted SuccessFully")
    return redirect('Vehicle:owner_dashboard')

@login_required
def slot_book(request, id):
    bunker = get_object_or_404(AddBunker, id=id)

    if request.method == 'POST':
        vehicle_number = request.POST.get('vehicle_number')
        mobile_number = request.POST.get('mobile_number')
        booking_date = request.POST.get('booking_date')
        time_slot = request.POST.get('time_slot')

        Booking.objects.create(
            user=request.user,
            bunker=bunker,
            vehicle_number=vehicle_number,
            mobile_number=mobile_number,
            booking_date=booking_date,
            time_slot=time_slot,
            status='pending'
        )

        messages.success(request, f"✅ Slot booked successfully for {bunker.bunker_name} on {booking_date}!")
        return redirect('Vehicle:index')

    return render(request, 'Vehicle/slot_book.html', {'bunker': bunker})

def add_mechanic(request):
    if request.method == "POST":
        name = request.POST['name']
        phone = request.POST['phone']
        experience = request.POST['experience']
        specialization = request.POST['specialization']
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Choose another one.")
            return redirect('Vehicle:add_mechanic')

        user = User.objects.create_user(
            username=username,
            password=password,
            user_type='mechanic',
            phone=phone 
        )

        Mechanic.objects.create(
            owner=request.user,
            user=user,
            name=name,
            phone=phone,
            experience=experience,
            specialization=specialization
        )

        messages.success(request, "Mechanic added successfully ✅")
        return redirect('Vehicle:owner_dashboard')

    return render(request, 'Vehicle/add_mechanic.html')

def delete_mechanic(request,id):
    mechanic = get_object_or_404(Mechanic,id=id)
    mechanic.delete()
    messages.success(request,"Mechanic Deleted SuccessFully")
    return redirect("Vehicle:owner_dashboard")

def service_page(request):
    mechanics = Mechanic.objects.all()
    users = CustomUser.objects.filter(user_type = 'user')
    owners = CustomUser.objects.filter(user_type = 'owner')
    bunkers = AddBunker.objects.all()
    return render(request,"Vehicle/service_page.html",{
        'mechanics':mechanics,
        'users':users,
        'bunkers':bunkers,
        'owners':owners
        
        })


def contact_message(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            ContactMessage.objects.create(name = name,email = email,message = message)
            return redirect("Vehicle:index")
        else:
            messages.error(request,"Please Fill Fields")
    return render(request,"Vehicle/contact_message.html")

def delete_message(request,id):
    msg = get_object_or_404(ContactMessage,id=id)
    msg.delete()
    messages.success(request,"Message Deleted")
    return redirect("Vehicle:admin_dashboard")

# from Vehicle.models import CustomUser
# for u in CustomUser.objects.all():
#     print(u.username, u.user_type)
