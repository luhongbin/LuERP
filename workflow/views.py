# coding=utf-8
from django.contrib.admin import site
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http.response import HttpResponseRedirect
from django.utils.encoding import force_text
from django.template.response import TemplateResponse
from django.contrib import messages
from django.contrib.auth.models import User
from workflow.models import Modal,Instance,TodoList,History,Node
from plugin.wfnodes import NextNodeManager,NextNodeHandler
from plugin.wfusers import NextUserManager,NextUserHandler
from plugin.wfactions import WorkflowActionManager,WorkflowAction


SELECTED_CHECKBOX_NAME = 'NEXT_NODE_USER'


def compile_node_handler(request,obj,next_node,object_id):
    """
    :param request:
    :param obj:
    :param handler:
    :return:
    """
    handler = next_node.handler
    next_user_handler = next_node.next_user_handler
    # next_user_handler 具有最高优先级
    if next_user_handler:
        print('it is here',next_user_handler)
        klass = NextUserManager().handlers.get(next_user_handler)
        if klass and isinstance(klass,NextUserHandler):
            return klass.handle(request,obj,next_node)

    if handler and handler != '':
        handler = handler.replace("submitter()", request.user.username)
        handler = handler.replace("suber()", request.user.username)
        fields = obj._meta.fields
        for field in fields:
            name = field.name
            temp = "{{%s}}" % name
            val = getattr(obj,name,None)
            if val:
                if type(val)!=str:
                    val = str(val)
                handler = handler.replace(temp,val)
        cursor = connection.cursor()
        print('track:',handler,object_id)

        if handler[0:3]=='CG:':
            users = []
            handler = 'select  pmdg002  from basedata_pmdg where id=%d limit 1' % (int(object_id))
            cursor.execute(handler)
            xx=cursor.fetchone()
            # for user in cursor.fetchone():
            #     xx = '<User: '+user+'>'
            #     users.append(xx)
            query2 = User.objects.filter(username=xx[0])
            users = [User for User in query2.all()]
            # for employee in query2.all():
            #     users.append(employee.user)
            print('track4:', users,type(users))
            return users
        else:
            print('track1:',handler)
            cursor.execute(handler)
            users = [user for user in cursor.fetchone()]
        print('track3:',users)
        return users
    else:
        tp = next_node.handler_type
        if tp == 1 and next_node.users:
            # user

            users = [user for user in next_node.users.all()]
            print('users:',users,type(users),type( next_node.users.all()))
            return users
        elif tp == 2 and next_node.positions:
            # position
            users = []
            for position in next_node.positions.all():
                for employee in position.employee_set.all():
                    users.append(employee.user)
            return users
        elif tp == 3 and next_node.roles:
            # role
            users = []
            for role in next_node.roles.all():
                for user in role.users.all():
                    users.append(user)
            return users
        elif tp == 4:
            # submitter
            return request.user
        else:
            return None


def start(request,app,model,object_id):
    """

    :param request:
    :return:
    """
    print('start:',app,model,object_id)
    import datetime
    content_type = ContentType.objects.get(app_label=app, model=model)
    obj = content_type.get_object_for_this_type(id=int(object_id))
    title = "您确定？"
    opts = obj._meta
    objects_name = force_text(opts.verbose_name)
    has_workflow = False
    queryset = Modal.objects.filter(content_type=content_type, end__gt=datetime.date.today()).order_by('-end')
    cnt = queryset.count()
    workflow_modal = None
    next_node = None
    next_users = []
    has_next_user = False
    if cnt > 0:
        #鲁红斌20190618加入PMDG需要供应商提交审批
        has_workflow = True
        if model =='pmdg':
            cursor = connection.cursor()
            handler = 'select  pmdf002,ooag011,pmdg002,pmaal004  from basedata_pmdg where id=%d limit 1' % (int(object_id))
            cursor.execute(handler)
            xx = cursor.fetchone()
            if xx[2] != request.user.username:
                messages.warning(request, "对象只能由供应商["+xx[2]+"]提交审批，请联系供应商操作")
                has_workflow = False
                print("对象只能由采购员["+xx[1]+"]提交审批，请联系供应商操作,提示")
            # else:
            #     try:
            #         print("邮件开始")
            #
            #         from email.mime.text import MIMEText
            #         from email.utils import formataddr
            #         import smtplib
            #         from django.contrib.auth.models import User
            #         u = User.objects.get(username=xx[3])
            #
            #         my_user = 'finance@lutec.net'  # 收件人邮箱账号，我这边发送给自己
            #         my_sender = 'system@umenb.com'  # 发件人邮箱账号
            #         my_pass = 'seqhsqumamnxcafa'  # 发件人邮箱密码(当时申请smtp给的口令)
            #         try:
            #             msg = MIMEText(
            #                 '亲爱的供应商【' + xx[2] + '】你好：<br><p>我们邀请您使用LUTEC供应商管理平台：</p><p><a href="http://www.umenb.com:8000/admin/"'+app+'/'+model+'/'+object_id+'">宁波耀泰(集团)管理平台</a><br>对品名：'  + obj.imaal003+'，规格：' + obj.imaal004 + '<br>及时报价。<br><hr>技术支持：宁波耀泰(集团)，<a href=mailto:finance@lutec.net>客服邮箱</a></p>',
            #                 'html', 'utf-8')
            #         except Exception:
            #             print( '亲爱的供应商【' + xx[2] + '】你好：<br><p>我们邀请您使用LUTEC供应商管理平台：</p><p><a href="http://www.umenb.com:8000/admin/"'+app+'/'+model+'/'+object_id+'">宁波耀泰(集团)管理平台</a><br>对品名：'  + obj.imaal003+'，规格：' + obj.imaal004 + '<br>及时报价。<br><hr>技术支持：宁波耀泰(集团)，<a href=mailto:finance@lutec.net>客服邮箱</a></p>')
            #         msg['From'] = formataddr(["发件人昵称", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            #         msg['Subject'] = "LUTEC供应商平台通知："  # 邮件的主题，也可以说是标题
            #
            #         server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是465
            #         server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
            #         if len(u.email) > 5:
            #             my_user = my_user + ';' + u.email
            #         else:
            #             msg = MIMEText('供应商【' + xx[2] + '】邮箱不存在，请T100修改邮箱后，手动发送邮件给供应商登录平台</p>', 'html', 'utf-8')
            #         msg['To'] = formataddr(["收件人昵称", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            #         server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            #         server.quit()  # 关闭连接
            #         print('email ok')
            #
            #     except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
            #         print('email error')
            #         ret = False

        workflow_modal = queryset[0]
        query_start_node = workflow_modal.node_set.filter(start=1)
        query_first_node = workflow_modal.node_set.order_by('id')
        if query_start_node.count() > 0:
            next_node = query_start_node[0]
        elif query_first_node.count()>0:
            next_node = query_first_node[0]
        if next_node:
            next_users = compile_node_handler(request, obj, next_node,object_id)
            if len(next_users) > 0:
                has_next_user = True
    else:
        title = "未配置工作流模型"

    try:
        tmp = Instance.objects.get(modal=workflow_modal, object_id=object_id)
        messages.warning(request, "对象已提交审批，请勿重复提交")
        return HttpResponseRedirect("/admin/%s/%s/%s" % (app, model, object_id))
    except Exception:
        pass

    if request.POST.get("post"):
        val = request.POST.getlist(SELECTED_CHECKBOX_NAME)
        workflow_inst = Instance.objects.create(modal=workflow_modal,object_id=object_id,starter=request.user)
        workflow_inst.current_nodes.add(next_node)
        workflow_inst.save()
        workflow_history = History.objects.create(inst=workflow_inst,user=request.user)
        for user in User.objects.filter(id__in=val):
            todo = TodoList.objects.create(inst=workflow_inst,node=next_node,user=user,app_name=app,model_name=model)
        TodoList.objects.create(inst=workflow_inst,user=request.user,app_name=app,model_name=model,is_read=True,
                                read_time=datetime.datetime.now(),status=True)
        if next_node.status_field and next_node.status_value:
            try:
                # setattr(obj,next_node.status_field,next_node.status_value)
                setattr(obj,'status','1')
                obj.save()
            except Exception:
                pass
        messages.success(request, "工作流提交成功")
        return HttpResponseRedirect("/admin/%s/%s/%s" % (app, model, object_id))

    context = dict(
        site.each_context(request),
        title=title,
        opts=opts,
        objects_name=objects_name,
        object=obj,
        has_workflow=has_workflow,
        workflow_modal=workflow_modal,
        next_node=next_node,
        has_next_user=has_next_user,
        next_users=next_users,
        checkbox_name=SELECTED_CHECKBOX_NAME,
    )
    request.current_app = site.name

    return TemplateResponse(request,'default/workflow/workflow_start_confirmation.html', context)


def approve(request,app,model,object_id,operation):
    """

    :param request:
    :param operation:
    :return:
    """
    if operation not in ('1','3','4'):
        messages.warning(request,"不识别的工作流操作")
        return HttpResponseRedirect("/admin/%s/%s/%s"%(app,model,object_id))

    import datetime
    import copy
    content_type = ContentType.objects.get(app_label=app,model=model)
    obj = content_type.get_object_for_this_type(id=int(object_id))
    title = "你确定？"
    opts = obj._meta
    objects_name = force_text(opts.verbose_name)

    has_workflow = False
    queryset = Modal.objects.filter(content_type=content_type,end__gt=datetime.date.today()).order_by('-end')
    cnt = queryset.count()
    workflow_modal = None
    if cnt > 0:
        workflow_modal = queryset[0]
    else:
        messages.warning(request, "未配置工作流模型")
        return HttpResponseRedirect("/admin/%s/%s/%s"%(app,model,object_id))
    workflow_instance = None
    try:
        workflow_instance = Instance.objects.get(modal = workflow_modal,object_id=object_id)
    except Exception:
        messages.warning(request,"请先启动工作流")
        return HttpResponseRedirect("/admin/%s/%s/%s"%(app,model,object_id))

    next_nodes = []
    node_users = []
    is_stop_node = False
    node_has_users = False
    delete_instance = False
    deny_to_first = False
    next_node_description = None
    all_nodes =[x for x in Node.objects.filter(modal=workflow_modal).order_by('-id')]
    current = workflow_instance.current_nodes.all()
    current_tmp = copy.deepcopy(current[0])
    if operation == '4' or operation == '3':
        next_nodes = ['stop']
        is_stop_node = True
    else:
        if current.count() > 1:
            pass
        else:
            tmp_node = current[0]
            if tmp_node.stop or tmp_node == all_nodes[0]:
                next_nodes = ['stop']
                is_stop_node = True
            else:
                if tmp_node.next_node_handler and len(tmp_node.next_node_handler) > 0:
                    hd = tmp_node.next_node_handler
                    klass = NextNodeManager().handlers.get(hd)
                    if klass and isinstance(klass,NextNodeHandler):
                        next_nodes = klass.handle(request,obj,tmp_node)
                        next_node_description = klass.description
                if next_nodes and len(next_nodes) > 0:
                    pass
                elif tmp_node.next and tmp_node.next.count()>0:
                    next_nodes = [nd for nd in tmp_node.next.all()]
                else:
                    position = all_nodes.index(tmp_node)
                    next_nodes = [all_nodes[position-1]]

    if request.POST.get("post"):
        from django.db import transaction
        val = request.POST.getlist(SELECTED_CHECKBOX_NAME)
        memo = request.POST['memo']
        with transaction.atomic():
            try:
                if delete_instance:
                    workflow_instance.delete()
                else:
                    if is_stop_node:
                        workflow_instance.status = 99
                        if operation in ('3', '4'):
                            workflow_instance.status = int(operation)
                        if not workflow_instance.approved_time and operation == '1':
                            workflow_instance.approved_time = datetime.datetime.now()
                        workflow_instance.current_nodes.clear()
                        workflow_instance.save()
                    else:
                        workflow_instance.current_nodes.clear()
                        workflow_instance.current_nodes.add(next_nodes[0])
                        for user in User.objects.filter(id__in=val):
                            todo = TodoList.objects.create(inst=workflow_instance,node=next_nodes[0],user=user,app_name=app,model_name=model)
                        if current_tmp.status_field and current_tmp.status_value:
                            try:
                                setattr(obj, current_tmp.status_field, current_tmp.status_value)
                                obj.save()
                                print('ok status',current_tmp.status_field, current_tmp.status_value)
                            except Exception:
                                print('ok error',current_tmp.status_field, current_tmp.status_value)
                                pass
                    # setattr(obj, 'status', '2')
                    # obj.save()
                    History.objects.create(inst=workflow_instance,user=request.user,pro_type=int(operation),memo=memo,node=current_tmp)
                    TodoList.objects.filter(inst=workflow_instance,node=current_tmp,status=0).update(status=1)
                messages.success(request, "工作流审批成功")
            except Exception as e:
                messages.error(request, e)
                pass
            if current_tmp.action and len(current_tmp.action) > 0:
                action = WorkflowActionManager().actions.get(current_tmp.action)
                if action and isinstance(action,WorkflowAction):
                    action.action(request,obj,current_tmp,object_id,operation)

        return HttpResponseRedirect("/admin/%s/%s/%s"%(app,model,object_id))

    if len(next_nodes) > 0 and not is_stop_node and operation == '1':
        for node in next_nodes:
            users = compile_node_handler(request, obj, node,object_id)
            if len(users) > 0:
                node_has_users = True
            node_users.append({'node': node, 'users': users})

    context = dict(
        site.each_context(request),
        title=title,
        opts=opts,
        objects_name=objects_name,
        object=obj,
        operation=operation,
        is_stop_node=is_stop_node,
        delete_instance=delete_instance,
        node_users=node_users,
        node_has_users=node_has_users,
        checkbox_name=SELECTED_CHECKBOX_NAME,
    )
    if next_node_description:
        context.update(dict(next_node_description=next_node_description))
    return TemplateResponse(request, "default/workflow/workflow_approve_confirmation.html",context)


def restart(request, app, model, object_id, instance):
    """

    :param request:
    :param app:
    :param model:
    :param object_id:
    :return:
    """
    try:
        inst = Instance.objects.get(id=int(instance))
        if request.user == inst.starter:
            inst.delete()
            messages.success(request, "重启工作流成功")
        else:
            messages.warning(request, "你没有重启工作流权限，发起者有权限")
    except Exception as e:
        messages.error(request, e)
    return HttpResponseRedirect("/admin/%s/%s/%s" % (app, model, object_id))