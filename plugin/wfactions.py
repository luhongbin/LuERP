# created at 15-6-30 
# coding=utf-8
__author__ = 'zhugl'
from django.db import connection
import string
class Operation(object):
    APPROVE = 1
    DENY = 3
    TERMINATE = 4


class WorkflowAction(object):

    name = ''
    description = ''

    def action(self,request,obj,node_config,object_id,operation=Operation.APPROVE):
        """

        :param request:
        :param obj:
        :param node_config:
        :return:
        """
class pmdgsaveAction(WorkflowAction):
    name = 'action.pmdgsave'

    def action(self,request,obj,node_config,object_id,operation=Operation.APPROVE):
        from basedata.models import pmdg
        obj.objects.save()

class TestAction(WorkflowAction):
    name = 'action.test'

    def action(self,request,obj,node_config,object_id,operation=Operation.APPROVE):
        from basedata.models import pmdg
        pmdg.objects.filter(id=object_id).update(status='3')
        cursor = connection.cursor()

        print ('this is a workflow test action')
        handler = 'select pmdgsite,pmdgdocno ,pmdgseq ,pmdgua006,pmdg009,pmdgud017,pmdgud014,pmdg013,pmdgua007,pmdgud013,pmdgud012,pmdg030, pmdgud015,pmdgud017,pmdgud018,pmdgud019,pmdgud020,pmdgud011,pmdg002 from basedata_pmdg where id=%d limit 1' % (int(obj.id))
        cursor.execute(handler)
        XX = cursor.fetchone()
        r0 = XX[0][:2]
        r1 = XX[1]
        r2 = int(XX[2])
        r3 = XX[3]
        r4 = XX[4]
        if r4==False:
            r4='N'
        else:
            r4 = 'Y'

        r5 = XX[5]
        r6 = XX[6]
        r7 = XX[7]
        r8 = XX[8]
        r9 = XX[9]
        r10 = XX[10]
        r11 = XX[11]
        if r11=='None':
            r11 = ''
        print('会写oracle:', r3,r4, r5, r6, r7, r8, r9, r10, r11, r0, r1, r2)
        r15 = XX[12]
        if r15 is None:
            r15 = 0
        r16 = XX[13]
        if r16 is None:
            r16 = 0
        r17 = XX[14]
        if r17 is None:
            r17 = 0
        r18 = XX[15]
        if r18 is None:
            r18 = 0
        r19 = XX[16]
        if r19 is None:
            r19 = 0
        r20 = XX[17]
        if r20 is None:
            r20 = 0

        r21 = XX[18]
        print('写oracle:', r15,r16, r17, r18, r19, r20,r21)

        cursor.close()
        # try:
        import cx_Oracle
        conn2 = cx_Oracle.connect('dsdata/dsdata@192.168.0.5:1521/TOPPRD')
        cur = conn2.cursor()
        print('oracle begin')

        handler = "update pmdg_t SET pmdgua007=('%f') where pmdgsite=('%s') and pmdgdocno=('%s') and pmdgseq=('%f') and pmdg002=('%s')" % (r8,  r0, r1, r2, r21)
        print(handler)
        cur.execute(handler)
        conn2.commit()  # 执行插入
        print('oracle ok0')

        handler = "update pmdg_t SET pmdgud015=('%f'),pmdgud017=('%f'),pmdgud018=('%f'),pmdgud019=('%f'),pmdgud020=('%f'),pmdgud011=('%f') where pmdgsite=('%s') and pmdgdocno=('%s') and pmdgseq=('%d') and pmdg002=('%s')" % ( r15, r16,r17, r18, r19, r20, r0, r1, r2, r21)
        cur.execute(handler)
        conn2.commit()  # 执行插入
        print('oracle ok1')

        handler = "update pmdg_t SET  pmdgua006=('%s') ,pmdg009=('%s') ,pmdgud017=('%s') ,pmdgud014=('%d') ,pmdg013=('%d') where pmdgsite=('%s') and pmdgdocno=('%s') and pmdgseq=('%d')  and pmdg002=('%s')" % ( r3,r4, r5, r6,r7,r0, r1, r2,r21)
        cur.execute(handler)
        conn2.commit()  # 执行插入
        print('oracle ok2')

        handler = "update pmdg_t SET  pmdgua006=('%s') ,pmdg009=('%s') ,pmdgud017=('%s') ,pmdgud014=('%f') ,pmdg013=('%f') ,pmdgua007=('%f') ,pmdgud013=('%f') ,pmdgud012=('%d') ,pmdg030=('%s') where pmdgsite=('%s') and pmdgdocno=('%s') and pmdgseq=('%d') and pmdg002=('%s')" % ( r3,r4, r5, r6, r7, r8, r9, r10, r11, r0, r1, r2,r21)
        cur.execute(handler)
        conn2.commit()  # 执行插入

        ##########从T100询价单中获取数据转让POSTGRESQL
        xxx = "select pmdgsite 公司别,pmdgdocno 询价单号,pmdgseq 项次,decode(pmdg001,'Y','外加工','采购') 属性,pmdg002 供应商编号,pmaal004 供应商简称,pmdg003 品号,imaal003 品名,imaal004 规格,pmdgua006 报价分类, pmdg007 询价数量,pmdg008 询价单位,pmdg009 分量计价否,pmdg011 税率,pmdgud014 最小包装量,pmdg013 最低采购量,pmdgua007 产品报价含税,pmdgud013 理论重量首次报价,pmdgud012 模具费报价含税,pmdg017 有效日期,pmdg030 计价公式及备注,pmdf002 工号,ooag011 姓名,pmdgud017,pmdgud005,pmdgud018,pmdgud019,pmdgud020 from dsdata.pmdg_t left join dsdata.pmdf_t on pmdfent=pmdgent and pmdfdocno=pmdgdocno left join dsdata.pmaal_t on pmaalent=pmdgent and pmaal001=pmdg002 and pmaal002='zh_CN' left join dsdata.imaal_t on imaal001 =pmdg003 and imaalent=pmdgent  and imaal002='zh_CN' left join dsdata.ooag_t  on pmdf002=ooag001 and ooagent=pmdgent where pmdgsite=('%s') and pmdgdocno=('%s') and pmdgseq=('%d') and pmdg002=('%s') "% ( r0, r1, r2,r21)
        cur.execute(xxx)
        res = cur.fetchall()
        for tao in res:
            r0 = tao[0]
            if r0 == 'Y1':
                r0 = 'Y1-耀泰'
            if r0 == 'Y3':
                r0 = 'Y3-颐道'
            r1 = tao[1]
            r2 = str(tao[2])
            print(r0, r1, r2)

            r3 = tao[3]
            r4 = tao[4]
            r5 = tao[5]
            r6 = tao[6]
            r7 = tao[7]
            if r7 is None:
                r7 = ''
            r8 = tao[8]
            if r8 is None:
                r8 = ''
            r9 = tao[9]
            if r9 is None:
                r9 = 1
            if r9 == '0':
                r9 = 1
            else:
                r9 = 2
            r10 = tao[10]
            r11 = tao[11]
            r12 = tao[12]
            r19 = tao[19].strftime("%Y%m%d")
            r20 = tao[20]
            r21 = tao[21]
            r22 = tao[22]
            r23 = tao[23]
            if r23 is None:
                r23 = 0
            r24 = tao[24]
            r25 = tao[25]
            r26 = tao[26]
            r27 = tao[27]
            r13 = tao[13]
            r14 = tao[14]
            r15 = tao[15]
            r16 = tao[16]
            r17 = tao[17]
            r18 = tao[18]
            print('read1',r19, r20, r21, r22, r23, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r0, r1, r2)
            print('read2:', r13, r14, r15, r16, r17, r18)
            print('read3:', r24, r25, r26, r27,r21)

        print('oracle ok')
        cur.close()
        conn2.close()
        # except:
        #     print('oracle bad')
        #print ('request user is %s,current node is %s')%(request.user,node_config)


class WorkflowActionManager(object):
    """
    """
    actions = {}
    registed = False

    def __init__(self):
        if WorkflowActionManager.registed:
            pass
        else:
            WorkflowActionManager.register(TestAction)
            WorkflowActionManager.register(pmdgsaveAction)
            WorkflowActionManager.registed = True

    @classmethod
    def register(cls,action):
        if cls.actions.get(action.name):
            raise Exception('%s already exists,register failed'%action.name)
        if issubclass(action,WorkflowAction):
            WorkflowActionManager.actions[action.name] = action()