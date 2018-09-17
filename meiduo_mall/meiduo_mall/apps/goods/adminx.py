import xadmin
from xadmin import views

from . import models


class BaseSetting(object):
    """xadmin的基本配置"""
    enable_themes = True  # 开启主题切换功能
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView, BaseSetting)


class GlobalSettings(object):
    """xadmin的全局配置"""
    site_title = "美多商城运营管理系统"  # 设置站点标题
    site_footer = "美多商城集团有限公司"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠


xadmin.site.register(views.CommAdminView, GlobalSettings)


class SKUAdmin(object):
    # 给该模型类增加图标
    model_icon = 'fa fa-gift'
    # 指定该模型类显示的字段
    list_display = ['id', 'name', 'price', 'stock', 'sales', 'comments']


xadmin.site.register(models.GoodsCategory)
xadmin.site.register(models.GoodsChannel)
xadmin.site.register(models.Goods)
xadmin.site.register(models.Brand)
xadmin.site.register(models.GoodsSpecification)
xadmin.site.register(models.SpecificationOption)
xadmin.site.register(models.SKU, SKUAdmin)
xadmin.site.register(models.SKUSpecification)
xadmin.site.register(models.SKUImage)

"""
admin的语法
    admin.site.register(models.SKUImage)

xadmin的语法
    xadmin.site.register(models.SKUImage)
"""