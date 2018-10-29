from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from goods.models import *
from redis import StrictRedis
from django.core.paginator import Paginator

def index(request):
    goods_list = GoodsType.objects.all()
    # sku=GoodsSKU.objects.all()
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
    for type in goods_list:
        image_banners = IndexTypeGoodBanner.objects.filter(type=type,display_type=1).order_by('index')
        title_banners = IndexTypeGoodBanner.objects.filter(type=type,display_type=0).order_by('index')
        type.image_banners=image_banners
        type.title_banners=title_banners
    cart_count = 0
    ret={
        "goods_list":goods_list,
        "goods_banners":goods_banners,
        "promotion_banners":promotion_banners,
        "cart_count":0
        }
    return render(request,'goods_list/index.html',ret)
def detail(request):
    goods_list = GoodsType.objects.all()
    sku_list=GoodsSKU.objects.all()
    len_sku_list=len(sku_list)-1
    sku_id=request.GET.get('id')
    sku=GoodsSKU.objects.get(id=sku_id)
    type=GoodsType.objects.get(id=sku.type_id)
    goods_image=GoodsImage.objects.get(sku_id=sku_id)
    new_skus=GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]
    same_spu_skus=GoodsSKU.objects.filter(goods_id=sku.goods_id).exclude(id=sku_id)
    user = request.user
    show_comment=GoodSComment.objects.filter(sku_id=sku_id)
    write_comment = request.POST.get('write_comment')
    comment_sku_id=sku_id
    comment_user_id=user.id
    if write_comment:
        GoodSComment.objects.create(comments=write_comment,sku_id=comment_sku_id,username_id=comment_user_id)
    if user.is_authenticated():
        conn=StrictRedis('192.168.12.196')
        history_key = 'histort_%d'%user.id
        conn.lrem(history_key,0,sku_id)
        conn.lpush(history_key,sku_id)
        conn.ltrim(history_key,0,4)
    ret={
        "goods_list": goods_list,
        "sku":sku,
        "type":type,
        "goods_image":goods_image,
        "sku_list":sku_list,
        "len_sku_list":len_sku_list,
        "new_skus":new_skus,
        "same_spu_skus":same_spu_skus,
        "show_comment":show_comment,
    }
    return render(request, 'goods_list/detail.html',ret)
def cart(request):
    return render(request, 'goods_list/cart.html')
def list(request):
    goods_list = GoodsType.objects.all()
    type_id=request.GET.get('type')
    type_object=GoodsType.objects.get(id=type_id)
    page=request.GET.get('pn')
    sort=request.GET.get('sort')
    if sort == 'price':
        skus=GoodsSKU.objects.filter(type_id=type_id).order_by('price')
    elif sort == 'hot':
        skus=GoodsSKU.objects.filter(type_id=type_id).order_by('-sales')
    else:
        sort == 'default'
        skus=GoodsSKU.objects.filter(type_id=type_id).order_by('-id')
    paginator =Paginator(skus,1)
    page = int(page)
    if page > paginator.num_pages:
        page = 1
    skus_page=paginator.page(page)
    num_pages = paginator.num_pages
    if num_pages < 5:
        pns = range(1,num_pages + 1)
    elif page <=3:
        pns = range(1,6)
    elif num_pages-page <=2:
        pns = range(num_pages-4,num_pages+1)
    else:
        pns = range(page-2,page+3)
    new_skus = GoodsSKU.objects.filter(type_id=type_id).order_by('-create_time')[:2]
    ret={
        "goods_list":goods_list,
        "new_skus":new_skus,
        "skus_pages":skus_page,
        "sort":sort,
        "type_id":type_id,
        "pns":pns,
        "type_object":type_object
    }
    return render(request, 'goods_list/list.html',ret)

