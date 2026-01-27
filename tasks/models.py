from django.db import models

from django.db.models.enums import TextChoices, IntegerChoices
from django.utils.translation import gettext_lazy as _


class TaskMode(TextChoices):
    FULL = "full", _("全量")
    PART = "part", _("部分")


class TaskType(TextChoices):
    REPORT = "report", _("报表生成")
    CLEANUP = "cleanup", _("清理任务")
    DATA_SYNC = "data_sync", _("数据同步")


class TaskStatus(IntegerChoices):
    WAIT = 0, _("等待中")
    RUNNING = 1, _("运行中")
    SUCCESS = 2, _("成功")
    FAIL = 3, _("失败")
    PART = 4, _("部分成功")
    TIMEOUT = 5, _("超时")


class DataOperationType(models.TextChoices):
    """操作类型枚举"""
    QUERY = 'query', _('查询')
    CREATE = 'create', _('创建')
    UPDATE = 'update', _('更新')
    DELETE = 'delete', _('删除')


class TaskInfo(models.Model):
    """任务信息表"""
    # 基础字段
    task_type = models.CharField(max_length=64, choices=TaskType.choices, verbose_name='任务类型')
    task_name = models.CharField(max_length=128, verbose_name='任务名称')
    task_mode = models.CharField(max_length=32, choices=TaskMode.choices, verbose_name='任务模式')
    task_desc = models.CharField(max_length=512, default="", verbose_name='任务描述')
    task_status = models.CharField(default=TaskStatus.WAIT, choices=TaskStatus.choices, verbose_name='任务状态')
    # 数据
    data_type = models.CharField(max_length=64, verbose_name='数据类型')
    # JSON 字段存储灵活配置
    task_params = models.JSONField(default=dict, verbose_name='任务参数')
    task_statistics = models.JSONField(default=dict, verbose_name='任务统计结果')
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    @property
    def duration_ms(self):
        """执行耗时(毫秒)"""
        return int((self.updated_at - self.created_at).total_seconds() * 1000)

    class Meta:
        db_table = 'task_info'
        verbose_name = '任务信息'

        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.data_type} - {self.task_type}] {self.task_name}"


class TaskRecord(models.Model):
    """任务记录表"""
    # 关联关系
    task = models.ForeignKey(TaskInfo, on_delete=models.CASCADE, related_name='records', verbose_name='关联任务'
    )
    # '冗余字段，避免JOIN查询'
    task_name = models.CharField(max_length=128, verbose_name=_('任务名称'), db_index=True)
    task_status = models.CharField(verbose_name=_('任务状态'), choices=TaskStatus.choices, default=TaskStatus.WAIT)
    # 数据
    data_type = models.CharField(verbose_name=_('数据类型'), max_length=64)
    data_operation = models.CharField(verbose_name=_('数据操作类型'), max_length=64,
                                      choices=DataOperationType.choices,
                                      default=DataOperationType.QUERY)
    data_unique_key = models.CharField(verbose_name=_('数据唯一键'), max_length=256)
    data = models.JSONField(verbose_name=_('数据结果'), default=dict())
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'task_record'
        verbose_name = '任务记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task_name} - {self.data_operation} - {self.data_unique_key}"
