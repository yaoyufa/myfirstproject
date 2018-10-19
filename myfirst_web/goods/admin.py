from django.contrib import admin

from goods.models import *
admin.site.register(Goods)
admin.site.register(GoodsImage)
admin.site.register(GoodsSKU)
admin.site.register(GoodsType)
