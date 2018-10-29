from django.shortcuts import render,redirect
from order.models import *
from user.models import *
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.conf import settings
from goods.models import *
import datetime
import os
from alipay import AliPay
def place(request):
    user = request.user
    sku_ids = request.POST.getlist('sku_ids')
    if not sku_ids:
        return redirect(reverse('goods:cart'))
    conn = settings.REDIS_CONN
    cart_key = 'cart_%d'%user.id
    skus = []
    total_count = 0
    total_price = 0
    for sku_id in sku_ids:
        sku = GoodsSKU.objects.get(id = sku_id)
        count = conn.hget(cart_key,sku_id)
        amount = sku.price*int(count)
        sku.amount = amount
        sku.count = count
        skus.append(sku)

        total_count += int(count)
        total_price += amount
    transit_price = 10
    total_pay = total_price + transit_price
    addrs=Address.objects.filter(a_username=user.id)
    sku_ids = ','.join(sku_ids)
    context = {
        'total_count':total_count,
        'total_price':total_price,
        'skus':skus,
        'transit_price':transit_price,
        'total_pay':total_pay,
        'addrs':addrs,
        'sku_ids':sku_ids,
    }
    return render(request,'order/place_order.html',context)
def order_commit(request):
    user = request.user
    if not user.is_authenticated():
        return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    sku_ids = request.POST.get('sku_ids')
    if not all([addr_id, pay_method, sku_ids]):
        return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
    try:
        addr = Address.objects.get(id=addr_id)
    except Address.DoesNotExist:
        return JsonResponse({'res': 3, 'errmsg': '地址非法'})
    order_id = datetime.datetime.today().strftime('%Y%m%d%H%M%S') + str(user.id)
    transit_price = 10
    total_count = 0
    total_price = 0
    try:
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            addr=addr,
            pay_method=pay_method,
            total_price=total_price,
            total_count=total_count,
            transit_price=transit_price,
        )
        conn = settings.REDIS_CONN
        cart_key = 'cart_%d' % user.id
        sku_ids = sku_ids.split(',')
        for sku_id in sku_ids:
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except:
                return JsonResponse({'res': 4, 'errsmg': '商品不存在'})

            count = conn.hget(cart_key, sku_id)
            if int(count) > sku.stock:
                return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=count,
                price=sku.price
            )
            sku.stock -= int(count)
            sku.sales += int(count)
            sku.save()

            amount = sku.price * int(count)
            total_count += int(count)
            total_price += amount

        order.total_count = total_count
        order.total_price = total_price

        order.save()

    except Exception as e:
        return JsonResponse({'res': 7, 'errmsg': '下单失败'})
    for i in sku_ids:
        conn.hdel(cart_key,i)
    return JsonResponse({'res':5,'message':'创建成功'})
def pay(request):
    user = request.user
    if not user.is_authenticated():
        return JsonResponse({'res':0,'errmsg':'用户未登录'})
    order_id = request.POST.get('order_id')
    print(order_id)
    if not order_id:
        return JsonResponse({'res':1,'errmsg':'无效的订单id'})
    try:
        print('order_id:%s'%order_id)
        order = OrderInfo.objects.get(order_id=order_id,
                                      user = user,
                                      pay_method=3,
                                      order_status=1)
    except OrderInfo.DoesNotExist:
        return JsonResponse({'res':2,'errmsg':'订单错误'})

    app_private_key_sting = os.path.join(settings.BASE_DIR,'order/app_private_key_pem')
    alipay_public_key_sting = os.path.join(settings.BASE_DIR,'order/app_public_key_pem')

    alipay = AliPay(
        appid= '2016092000551740',
        app_notify_url = None,
        app_private_key_path= app_private_key_sting,
        alipay_public_key_path= alipay_public_key_sting,
        sign_type='RSA2',
        debug= True
    )

    subject = '天天生鲜订单-%s'%order.order_id
    total_pay = order.total_price + order.transit_price

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount= str(total_pay),
        subject=subject,
        return_url=None,
        notify_url=None
    )
    pay_url = 'https://openapi.alipaydev.com/gateway.do?'+order_string
    return JsonResponse({'res':3,'pay_url':pay_url})
def checkpay(request):
        # 用户是否登录
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res':0,'errmsg':'请先登录'})

        # 接收参数
        order_id = request.POST.get('order_id')

        #  校验参数
        if not order_id:
            return JsonResponse({'res':1,'errmsg':'无效的订单'})
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except Exception as e:
            return JsonResponse({'res':2,'errmsg':'订单错误'})
        # 业务初始化:使用python sdk调用支付宝的支付接口
        # 初始化
        alipay = AliPay(
            appid="2016092000551740",  # 应用id
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'order/app_private_key_pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'order/app_public_key_pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        # 调用支付宝的交易查询接口
        while True:
            response = alipay.api_alipay_trade_query(order_id)
            code = response.get('code')

            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功
                # 获取支付宝交易号
                trade_no = response.get('trade_no')
                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 4  # 待评价
                order.save()
                # 返回结果
                return JsonResponse({'res': 3, 'message': '支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 等待买家付款
                # 业务处理失败，可能一会就会成功
                import time
                time.sleep(5)
                continue
            else:
                # 支付出错
                print(code)
                return JsonResponse({'res': 4, 'errmsg': '支付失败'})



