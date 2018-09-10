from django.contrib import admin

from . import models
# Register your models here.


class GoodsCategoryAdmin(admin.ModelAdmin):
    """定义GoodsCategory模型类的站点管理类
    用于监听保存和删除事件，触发异步任务
    """
    def save_model(self, request, obj, form, change):
        """
        监听站点的保存事件
        :param request: 本次保存时的请求
        :param obj: 本次保存时的模型对象
        :param form: 本次保存时操作的表单
        :param change: 本次保存时的数据跟旧数据的不同点
        :return: None
        """
        obj.save()
        from celery_tasks.html.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()

    def delete_model(self, request, obj):
        """
        监听站点的删除事件
        :param request: 本次删除时的请求
        :param obj: 本次删除时的模型对象
        :return: None
        """
        obj.delete()
        # 追加自己的触发异步任务的行为
        from celery_tasks.html.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()


admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)