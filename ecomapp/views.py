# from django.http import HttpResponse
from django.shortcuts import redirect, render, HttpResponse
from ecomapp.models import Product, Orders, OrderUpdate
from django.contrib import messages
from math import ceil
from ecomapp import keys
from django.conf import settings
MERCHANT_KEY=keys.MK
import json
from django.views.decorators.csrf import csrf_exempt
from Paytm import Checksum

# Create your views here.
def home(request):
    return render(request, 'index.html')

def tracker(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try again")
        return redirect('/ecomauth/login')
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id = orderId, email = email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id = orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{mo orders}')
        except Exception as e:
            return HttpResponse('{}')
    return render(request, 'tracker.html')

def purchase(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds':allProds}
    return render(request, 'purchase.html', params)

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/ecomauth/login')
    if request.method == "POST":

        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        Order_instance = Orders(items_json = items_json, name = name, amount = amount, email = email, address1 = address1, address2 = address2, city = city, state = state, zip_code = zip_code, phone = phone)
        print(amount)
        Order_instance.save()
        update = OrderUpdate(order_id=Order_instance.order_id, update_desc="the order has been placed")
        update.save()
        thank = True

# Payment integrations

        id = Order_instance.order_id
        oid = str(id)+"AISPACEX"
        param_dict = {

            'MID' : keys.MID,
            'ORDER_ID' : oid,
            'TXN_AMOUNT' : str(amount),
            'CUST_ID' : email,
            'INDUSTRY_TYPE_ID' : 'Retail',
            'WEBSITE' : 'WEBSTAGING',
            'CHANNEL_ID' : 'WEB',
            'CALLBACK_URL' : 'http://<your-ngrok-url>/handlerequest/',
        }

        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict':param_dict})
    
    return render(request, 'checkout.html')
        
@csrf_exempt
def handlerequest(request):

    # paytm wll send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('oredr successful')
            a = response_dict['ORDERID']
            b = response_dict['TXNAMOUNT']
            rid = a.replace("AISPACEX","")
            
            print(rid)
            filter2 = Orders.objects.filter(order_id = rid)
            print(filter2)
            print(a,b)
            for post1 in filter2:

                post1.oid = a
                post1.amountpaid = b
                post1.paymentstatus = "PAID"
                post1.save()
            print("run ageda function")
        else:
            print('order not successful because' + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response' : response_dict})