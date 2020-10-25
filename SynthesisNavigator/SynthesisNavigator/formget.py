from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators import csrf
from AppModel import models
from django.db.models import Q

# 接收请求数据
def formGet(request):
    '''
    获取表单数据
    '''
    request.encoding = 'utf-8'
    if request.method == 'GET' and request.GET:
        if 'q' in request.GET and request.GET['q']:
            try:
                message = '<d>你搜索的信息为:'+ models.Compound.objects.get(cid=str(request.GET['q'])).name
                message += '</d><p>它的属性如下所示：</p><p>'
                message = message + models.Compound.objects.get(cid=str(request.GET['q'])).cid + '  ' + models.Compound.objects.get(cid=str(request.GET['q'])).smile
                message += '</p>'
            except:message = '输入有误！'
        else:
            message = '你提交了空表单'
        return HttpResponse(message)

    elif request.method == 'POST' and request.POST:
        ctx = {}
        if request.POST:
            ctx['rlt'] = request.POST['q']
        return render(request, "post.html", ctx)

def vague_search():
    '''
    '''
    

