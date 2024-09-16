from os import name
from django.shortcuts import render,redirect
from . models import Product,Category,Profile
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from . forms import SignUpForm,UpdateUserForm,ChangePasswordForm,UserInfoForm
from django.db.models import Q
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress

def search(request):
    #check if user filled the form
    if request.method=="POST":
        searched=request.POST['searched']
        #Query the database for products
        searched=Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))

        if not searched:
            messages.warning(request,("Product does not exit search for another product"))
            return render(request,'search.html',{})
        else:
            return render(request,'search.html',{'searched':searched})
    return render(request,'search.html',{})


def update_info(request):
    if request.user.is_authenticated:
        #Original form
        current_user=Profile.objects.get(user__id=request.user.id)
        user_form=UserInfoForm(request.POST or None,instance=current_user)

        #Shipping form
        shipping_user=ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form=ShippingForm(request.POST or None,instance=shipping_user)

        if user_form.is_valid() or shipping_form.is_valid(): #
            user_form.save()
            shipping_form.save()
            login(request,current_user)
            messages.success(request,("User Info has been Updated"))
            return redirect("home")
        return render(request,'update_info.html',{'user_form':user_form,'shipping_form':shipping_form}) #

    else:
        messages.warning(request,("You must be logged in"))
        return redirect("home")


def update_password(request):

    if request.user.is_authenticated:
        current_user=request.user
        # did they fill the form 

        if request.method == "POST":
            form=ChangePasswordForm(current_user,request.POST)

            #IS form valid
            if form.is_valid():
                form.save()
                messages.success(request,("Your Password has been Updated........"))
                login(request,current_user)
                return redirect('update_user')
            
            else:
                for error in list(form.errors.values()):
                    messages.error(request,error)
                    return redirect('update_password')

        else:
            form=ChangePasswordForm(current_user)
            return render(request,'update_password.html',{'form':form})
        
    else:
        messages.warning(request,("You must be logged in......."))
        return redirect("home")


    return render(request,"update_password.html",{})


def update_user(request):
    if request.user.is_authenticated:
        current_user=User.objects.get(id=request.user.id)
        user_form=UpdateUserForm(request.POST or None,instance=current_user)

        if user_form.is_valid():
            user_form.save()
            login(request,current_user)
            messages.success(request,("User has been Updated"))
            return redirect("home")
        return render(request,"update_user.html",{"user_form":user_form})
    else:
        messages.warning(request,("You must be logged in"))
        return redirect("home")

    # return render(request,"update_user.html",{"user_form":user_form})


def category_summary(request):
    categories=Category.objects.all()


    return render(request,'category_summary.html',{"categories":categories})

def category(request,foo):
    foo=foo.replace('-',' ')
    #Grab the category from the url

    try:
        category=Category.objects.get(name=foo)
        products=Product.objects.filter(category=category)
        return render(request,'category.html',{'products':products,'category':category})

    except:
        messages.warning(request,("There was an error in logging"))
        return redirect('home')


def home(request):
    products=Product.objects.all()
    return render(request,'home.html',{'products':products})

def about(request):
    return render(request,'about.html',{})


def login_user(request):
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)

            #Do some3 shopping cart stuff

            current_user=Profile.objects.get(user__id=request.user.id)

            #Get their saved cart
            saved_cart=current_user.old_cart
            #convert DB string to python dict
            if saved_cart:
                #convert to dict using JSON
                converted_cart=json.loads(saved_cart)
                #Add the loaded cart dict to session
                cart=Cart(request)
                #loop through the cart and add the items from the DB
                for key,value in converted_cart.items():
                    cart.db_add(product=key,quantity=value)


            messages.success(request,("You have been Logged In"))
            return redirect('home')
        else:
            messages.warning(request,("There was an error in logging"))
            return redirect('login')
    return render(request,'login.html',{})

def logout_user(request):
    logout(request)
    messages.success(request,("You have een logged out...."))
    return redirect('home')


def register_user(request):
    form=SignUpForm()
    if request.method == "POST":
        form=SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')
            #log in user
            user=authenticate(username=username,password=password)
            login(request,user)
            messages.success(request,('Username Creted Please Update all the Info....'))
            return redirect('update_info')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
                return redirect('register')
    else:
        return render(request,'register.html',{'form':form})


def product(request,pk):
    product=Product.objects.get(id=pk)
    return render(request,'product.html',{'product':product})


