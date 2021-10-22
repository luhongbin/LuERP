# created at 15-6-30 
# coding=utf-8
__author__ = 'zhugl'


class NextUserHandler(object):
    """
    """
    name = ''
    description = ''

    def handle(self,request,obj,node_config):
        """

        :param request:
        :param obj:
        :param node_config:
        :return:django.contrib.auth.models.User[]
        """
        return None

class pmdg_cg(NextUserHandler):

    name = 'up.pmdg_cg.user'

    def handle(self,request,obj,node_config):
        users = []
        from django.contrib.auth.models import User

        query2 = User.objects.filter(username=obj.pmdg002)
        if query2.count() > 0:
            users = [User for User in query2.all()]
            return users
        else:
            return None

class pmdg_wofangcg(NextUserHandler):

    name = 'up.pmdg_wofangcg.user'

    def handle(self,request,obj,node_config):
        users = []
        from django.contrib.auth.models import User

        query2 = User.objects.filter(username=obj.pmdf002)
        if query2.count() > 0:
            users = [User for User in query2.all()]
            return users
        else:
            return None

class UpPosition(NextUserHandler):
    """

    """

    name = 'up.position.user'

    def handle(self,request,obj,node_config):
        from basedata.models import Employee,Position
        emp_query = Employee.objects.filter(user=request.user)
        if emp_query.count()>0:
            emp = emp_query.all()
            parent = []
            for e in emp:
                if e.position and e.position.parent:
                    parent.append(e.position.parent)
            # print emp
            # print parent
            query2 = Employee.objects.filter(position__in=parent).exclude(user=None)
            return [x.user for x in query2.all()]
        else:
            return None


class NextUserManager(object):
    """

    """
    handlers = {}
    registed = False

    def __init__(self):
        if NextUserManager.registed:
            pass
        else:
            NextUserManager.register(UpPosition)
            NextUserManager.register(pmdg_cg)
            NextUserManager.register(pmdg_wofangcg)
            NextUserManager.registed = True

    @classmethod
    def register(cls,handler):
        if cls.handlers.get(handler.name):
            raise Exception('%s already exists,register failed'%handler.name)
        if issubclass(handler,NextUserHandler):
            NextUserManager.handlers[handler.name] = handler()