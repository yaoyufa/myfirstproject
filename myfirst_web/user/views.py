from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from user.models import *
from django.contrib.auth import authenticate, login
from encrypt.md5 import my_md5
from django.core.urlresolvers import reverse
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from celery_tasks.task import task_celery_tasks
from myfirst_web import settings
from redis import StrictRedis
from django.contrib.auth import logout
from goods.models import *
from order.models import *

def userlogin(request):
    if request.method == "GET":
        a=reverse('user:login')
        print(a)
        remember_user_name = request.COOKIES.get("remember_user_name", "")
        return render(request, "user_list/login.html", {"remember_user_name": remember_user_name})
    elif request.method == "POST":
        user_name = request.POST.get("user_name", "").strip()
        user_pwd = request.POST.get("user_pwd", "").strip()
        validatecode = request.POST.get("validate_code", "").strip().lower()
        validate_code = request.session["validate_code"].strip().lower()
        remember_name = request.POST.get("remember_name")
        user=authenticate(username=user_name, password=user_pwd)
        if user is not None:
            if validatecode != validate_code:
                return render(request, "user_list/login.html")
            else:
                if user.is_active:
                    login(request,user)
                    # request.session["now_login_username"] = user_name
                    next_url=request.GET.get('next')
                    if next_url:
                        return HttpResponseRedirect(next_url)
                    else:
                        resp = redirect(reverse('goods:index'))
                        if remember_name == "1":
                            resp.set_cookie("remember_user_name", user_name, 3600 * 24 * 7)
                        else:
                            resp.set_cookie("remember_user_name", user_name, 0)
                        return resp
                else:
                    return HttpResponse('0')
        else:
            return render(request,"user_list/login.html",{"login_error":1})
def register(request):
    return render(request,"user_list/register.html")
def register_handle(request):
    if request.method == "GET":
        request_info = request.GET
    else:
        request_info = request.POST
    user_name = request_info.get("user_name")
    user_pwd = request_info.get("user_pwd")
    user_email=request_info.get("user_email")
    if User.objects.filter(username=user_name).exists():
        return HttpResponse(1)
    else:
        user=User.objects.create(username=user_name, password=my_md5(user_pwd),email=user_email,is_active=0)
        serializer =Serializer(settings.SECRET_KEY,3600)
        info={'confirm':user.id}
        token=serializer.dumps(info).decode()
        encryption_url='http://192.168.12.196:8888/user/active/%s'%token

        subject='天天生鲜欢迎主题'
        message =''
        sender = settings.EMAIL_FROM
        receive = [user_email]
        html_message='<h1>%s,欢迎你成为天天生鲜注册会员</h1>请点击激活账户<br/><a href="%s">%s</a>'%(user_name,encryption_url,encryption_url)
        task_celery_tasks.delay(subject,message,sender,receive,html_message)
        return HttpResponseRedirect(reverse("user:login"))
def active(request,token):
    serializer=Serializer(settings.SECRET_KEY,3600)
    try:
        info = serializer.loads(token)
        user_id =info['confirm']

        user= User.objects.get(id=user_id)
        user.is_active= 1
        user.save()
        return HttpResponseRedirect(reverse('user:login'))
    except SignatureExpired as e:
        return HttpResponse('激活链接已过期')
    except BadSignature as e:
        return HttpResponse('激活链接非法')
def validatecode(request):
    bgcolor = (255,255,255)
    width = 100
    height = 35
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    request.session["validate_code"]=rand_str
    # 构造字体对象
    font = ImageFont.truetype('NotoSansCJK-Black.ttc', 23)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    buf = BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    return HttpResponse(buf.getvalue(), 'image/png')
def user_center_info(request):
    user=request.user
    if user.is_authenticated():
        # if request.session['now_login_username']:
        #     user=User.objects.filter(username=request.session['now_login_username'])[0]
            user_address=user.user_address
            user_phone=user.user_phone
            comm=StrictRedis('192.168.12.196')
            sku_list=[]
            history = comm.lrange('histort_%d'%user.id,0,-1)
            for id in history:
                sku=GoodsSKU.objects.filter(id=id)[0]
                sku_list.append(sku)
            if user_phone:
                if user_address:
                    user_check = 1
            else:
                user_check = 0
            return render(request,'user_list/user_center_info.html',{"user_address":user_address,"user_phone":user_phone,"user_check":user_check,"sku_list":sku_list})
        # else:
        #     return render(request,'user_list/login.html')
def user_center_order(request):
    user =request.user
    order_info=OrderInfo.objects.filter(user_id=user.id)
    for order in order_info:
        order_goods=OrderGoods.objects.filter(order_id=order.order_id)
        order.goods=order_goods
        for i in order_goods:
            i.amount=i.count*i.price
    ret={
        "order_info":order_info,
    }
    return render(request,'user_list/user_center_order.html',ret)
def user_center_site(request):
    user = request.user
    if request.method == 'GET':
        a_username_id = user.id
        address=Address.objects.filter(a_username_id=a_username_id)
        address_list=[]
        for i in address:
            address_list.append(i)
        if request.GET.get('handle') == 'update':
            user_id = request.GET.get('id')
            address_update = Address.objects.filter(id=user_id)[0]
            user_recipient = address_update.user_recipient
            user_address_province=address_update.user_address.split('-')[0]
            user_address_province_id = AreaInfo.objects.filter(atitle=user_address_province)[0].id
            user_address_city=address_update.user_address.split('-')[1]
            user_address_city_id=AreaInfo.objects.filter(atitle=user_address_city)[0].id
            user_address_county = address_update.user_address.split('-')[2]
            user_address_detail = address_update.user_address.split('-')[3]
            user_postcode = address_update.user_postcode
            user_phone = address_update.user_phone
            return render(request, 'user_list/handle.html',{'user_recipient': user_recipient,'user_address_province':user_address_province,'user_address_city':user_address_city,
             'user_address_county':user_address_county,'user_address_detail': user_address_detail, 'user_postcode': user_postcode, 'user_phone': user_phone,'user_id':user_id,
              'user_address_city_id':user_address_city_id,'user_address_province_id':user_address_province_id})
        else:
            user_id = request.GET.get('id')
            if Address.objects.filter(id=user_id):
                address_update = Address.objects.filter(id=user_id)[0]
                address_update.delete()
            a_username_id = user.id
            address = Address.objects.filter(a_username_id=a_username_id)
            address_list = []
            for i in address:
                address_list.append(i)
            return render(request, 'user_list/user_center_site.html',{"address_list":address_list})
    elif request.method == 'POST':
        user_recipient = request.POST.get('user_recipient')
        province_id=request.POST.get('province')
        user_province=AreaInfo.objects.filter(id=province_id)[0].atitle
        city_id=request.POST.get('city')
        user_city=AreaInfo.objects.filter(id=city_id)[0].atitle
        county_id=request.POST.get('county')
        user_county=AreaInfo.objects.filter(id=county_id)[0].atitle
        user_address = request.POST.get('user_address')
        user_address=user_province+'-'+user_city+'-'+user_county+'-'+user_address
        user_postcode = request.POST.get('user_postcode')
        user_phone = request.POST.get('user_phone')
        a_username_id = user.id
        Address.objects.create(user_recipient=user_recipient, user_address=user_address, user_postcode=user_postcode,user_phone=user_phone, a_username_id=a_username_id)
        address=Address.objects.filter(a_username_id=a_username_id)
        address_list=[]
        for i in address:
            address_list.append(i)
        return render(request, 'user_list/user_center_site.html',{"address_list":address_list})
def forget(request):
    user_name=request.POST.get('user_name')
    user_email=request.POST.get('user_email')
    user_new_pwd=request.POST.get('new_pwd')
    user_check_pwd=request.POST.get('check_pwd')
    if User.objects.filter(username=user_name) and User.objects.filter(email=user_email):
        if user_new_pwd == user_check_pwd :
            user=User.objects.filter(username=user_name)[0]
            user.set_password(user_new_pwd)
            user.save()
            return HttpResponse('OK')
        else:
            return HttpResponse('输入不一致')
    else:
            return render(request,"user_list/forget.html")
def add_info(request):
    user=request.user
    if request.method == 'POST':
        user_address=request.POST.get('user_address')
        user_phone=request.POST.get('user_phone')
        user.user_phone=user_phone
        user.user_address=user_address
        user.save()
        userce=reverse('user:user_center_info')
        return HttpResponseRedirect(userce)
    elif request.method == 'GET':
        return render(request, 'user_list/add_info.html')
def userlogout(request):
        logout(request)
        return HttpResponseRedirect(reverse('goods:index'))
def handle(request):
    if request.method == 'POST':
        address_id = request.POST.get('id')
        address_update = Address.objects.filter(id=address_id)[0]
        address_update.user_recipient = request.POST.get('user_recipient')
        address_update.user_address.split('-')[0]=AreaInfo.objects.filter(id=request.POST.get('province'))[0].atitle
        address_update.user_address.split('-')[1] =AreaInfo.objects.filter(id=request.POST.get('city'))[0].atitle
        address_update.user_address.split('-')[2] =AreaInfo.objects.filter(id=request.POST.get('county'))[0].atitle
        address_update.user_address.split('-')[3] == request.POST.get('user_address')
        address_update.user_address=AreaInfo.objects.filter(id=request.POST.get('province'))[0].atitle+'-'+AreaInfo.objects.filter(id=request.POST.get('city'))[0].atitle+'-'+AreaInfo.objects.filter(id=request.POST.get('county'))[0].atitle+'-'+request.POST.get('user_address')
        address_update.user_postcode = request.POST.get('user_postcode')
        address_update.user_phone = request.POST.get('user_phone')
        address_update.save()
        return HttpResponseRedirect(reverse('user:user_center_site'))
def province(request):
    provinceList = AreaInfo.objects.filter(aParent__isnull=True)
    list1 = []
    for item in provinceList:
        list1.append([item.id, item.atitle])
    return JsonResponse({'data': list1})
def city(request, pid):
    cityList = AreaInfo.objects.filter(aParent_id=pid)
    list1 = []
    for item in cityList:
        list1.append([item.id, item.atitle])
    return JsonResponse({'data': list1})
def county(request, pid):
    countyList = AreaInfo.objects.filter(aParent_id=pid)
    list1 = []
    for item in countyList:
        list1.append([item.id, item.atitle])
    return JsonResponse({'data': list1})
