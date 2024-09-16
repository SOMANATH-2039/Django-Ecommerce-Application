from django.shortcuts import render,redirect
from cart.cart import Cart
from payment.forms import ShippingForm,PaymentForm
from payment.models import ShippingAddress,Order,Orderitem
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Product,Profile
import datetime


def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #get the order
        order=Order.objects.get(id=pk)
        items=Orderitem.objects.filter(order=pk)

        if request.POST:
            status=request.POST['shipping_status']
            if status=="true":
                order=Order.objects.filter(id=pk)
                now=datetime.datetime.now()
                order.update(shipped=True,date_shipped=now)
            else:
                order=Order.objects.filter(id=pk)
                order.update(shipped=False)

            messages.success(request,"Shipping Status Updated")
            return redirect('home')
        return render(request,'payment/orders.html',{'order':order,'items':items})
    
    else:
        messages.warning(request,"Access Denied")
        return redirect('home')


def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders=Order.objects.filter(shipped=True)
        if request.POST:
            status=request.POST['shipping_status']
            num=request.POST['num']
            now=datetime.datetime.now()
            order=Order.objects.filter(id=num)
            order.update(shipped=False,date_shipped=now)

            messages.success(request,"Shipping Status Updated")
            return redirect('home')
        return render(request,'payment/shipped_dash.html',{'orders':orders})
    
    else:
        messages.warning(request,"Access Denied")
        return redirect('home')


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders=Order.objects.filter(shipped=False)
        if request.POST:
            status=request.POST['shipping_status']
            num=request.POST['num']
            now=datetime.datetime.now()
            order=Order.objects.filter(id=num)
            order.update(shipped=True)
        
            messages.success(request,"Shipping Status Updated")
            return redirect('home')
        return render(request,'payment/not_shipped_dash.html',{'orders':orders})
    
    else:
        messages.warning(request,"Access Denied")
        return redirect('home')


def payment_success(request):
    return render(request,'payment/payment_success.html',{})


def checkout(request):
    cart=Cart(request)
    cart_products=cart.get_prods
    quantities=cart.get_quants
    totals=cart.cart_total()
    if request.user.is_authenticated:
        shipping_user=ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form=ShippingForm(request.POST or None,instance=shipping_user)

        return render(request,'payment/checkout.html',{'cart_products':cart_products,"quantities":quantities,"totals":totals,'shipping_form':shipping_form})

    else:
        shipping_form=ShippingForm(request.POST or None)

        return render(request,'payment/checkout.html',{'cart_products':cart_products,"quantities":quantities,"totals":totals,'shipping_form':shipping_form})


def billing_info(request):
    if request.POST:

        cart=Cart(request)
        cart_products=cart.get_prods
        quantities=cart.get_quants
        totals=cart.cart_total()

        #Create a Session with shipping info

        my_shipping=request.POST
        request.session['my_shipping']=my_shipping

        #check if user is logged in
        if request.user.is_authenticated:
            billing_form=PaymentForm()
            return render(request,'payment/billing_info.html',{'cart_products':cart_products,"quantities":quantities,"totals":totals,'shipping_info':request.POST,'billing_form':billing_form})
        else:
            billing_form=PaymentForm()
            return render(request,'payment/billing_info.html',{'cart_products':cart_products,"quantities":quantities,"totals":totals,'shipping_info':request.POST,'billing_form':billing_form})


        # shipping_form=request.POST

        # return render(request,'payment/billing_info.html',{'cart_products':cart_products,"quantities":quantities,"totals":totals,'shipping_form':shipping_form})
    else:
        messages.warning(request,"Access Denied")
        return redirect('home')
    

def process_order(request):
    if request.POST:
        cart=Cart(request)
        cart_products=cart.get_prods
        quantities=cart.get_quants
        totals=cart.cart_total()
        #get billing info from 
        payment_form=PaymentForm(request.POST or None)

        #Get shipping session data
        my_shipping=request.session.get('my_shipping')


        #GET order info
        full_name=my_shipping['shipping_full_name']
        email=my_shipping['shipping_email']
        # Create shippig address from sessionn info

        shipping_address=f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        ammount_paid=totals

        # Check if user is logged in or not
        if request.user.is_authenticated:
            user=request.user
            create_order=Order(user=user,full_name=full_name,email=email,shipping_address=shipping_address,ammount_paid=ammount_paid)
            create_order.save()

            #Add Order Items
            order_id=create_order.pk
            #Det Order ID
            for product in cart_products():
                product_id=product.id
                if product.is_sale:
                    price=product.sale_price
                else:
                    price=product.price

                for key,value in quantities().items():
                    if int(key)==product.id:
                        # Create Order Item
                        create_order_item=Orderitem(order_id=order_id,product_id=product_id,user=user,quantity=value,price=price)
                        create_order_item.save()
                        
            # Lets Delete our cart
            for key in list(request.session.keys()):
                if key=="session_key":
                    del request.session[key]
                    
            #Delete Cart from Database 
            current_user=Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")


            messages.warning(request,"Order Placed")
            return redirect('home')
            
        else:
            #Not logged in
            create_order=Order(full_name=full_name,email=email,shipping_address=shipping_address,ammount_paid=ammount_paid)
            create_order.save()

            #Add Order Items
            order_id=create_order.pk
            #Det Order ID
            for product in cart_products():
                product_id=product.id
                if product.is_sale:
                    price=product.sale_price
                else:
                    price=product.price

                for key,value in quantities().items():
                    if int(key)==product.id:
                        # Create Order Item
                        create_order_item=Orderitem(order_id=order_id,product_id=product_id,quantity=value,price=price)
                        create_order_item.save()
            # Lets Delete our cart
            for key in list(request.session.keys()):
                if key=="session_key":
                    del request.session[key]

            


            messages.warning(request,"Please Login to Continue")
            return redirect('home')

    else:
        messages.warning(request,"Access Denied")
        return redirect('home')
