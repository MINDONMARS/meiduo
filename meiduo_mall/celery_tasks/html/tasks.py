# from celery_tasks.main import celery_app
# from goods.utils import get_categories
# from django.template import loader
# from django.conf import settings
# import os
#
#
# @celery_app.task(name='generate_static_list_search_html')
# def generate_static_list_search_html():
#     """
#     生成静态的商品列表页和搜索结果的html文件
#     """
#     # 商品分类菜单
#     categories = get_categories()
#
#     context = {
#         'categories': categories
#     }
#     template = loader.get_template('list.html')
#     html_text = template.render(context)
#     file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'list.html')
#     with open(file_path, 'w') as f:
#         f.write(html_text)
from celery_tasks.main import celery_app
from django.template import loader
import os
from django.conf import settings

from goods.utils import get_categories


@celery_app.task(name='generate_static_list_search_html')
def generate_static_list_search_html():
    """
    生成静态的商品列表页和搜索结果页html文件
    """
    # 商品分类菜单
    categories = get_categories()

    # 渲染模板，生成静态html文件
    context = {
        'categories': categories,
    }

    # 渲染模板
    template = loader.get_template('list.html')
    html_text = template.render(context)

    # 将html字符串写入到html文件
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'list.html')
    with open(file_path, 'w') as f:
        f.write(html_text)