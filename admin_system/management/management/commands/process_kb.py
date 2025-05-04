"""
知识库处理命令 - 处理知识库内容并创建向量索引

此脚本用于处理知识库文档，进行分块并创建向量索引，以支持语义搜索。
"""
from django.core.management.base import BaseCommand
from pathlib import Path
from management.models import KnowledgeBase
from knowledge_base.services import process_knowledge_base
import os

class Command(BaseCommand):
    help = '处理知识库内容并创建向量索引'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='指定要处理的知识库ID'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='处理所有知识库'
        )
    
    def handle(self, *args, **options):
        kb_id = options.get('id')
        process_all = options.get('all')
        
        if kb_id:
            # 处理指定知识库
            try:
                kb = KnowledgeBase.objects.get(id=kb_id)
                self.stdout.write(f"正在处理知识库: {kb.name}")
                success = process_knowledge_base(kb_id)
                if success:
                    self.stdout.write(self.style.SUCCESS(f"知识库 {kb.name} 处理完成"))
                else:
                    self.stdout.write(self.style.ERROR(f"知识库 {kb.name} 处理失败"))
            except KnowledgeBase.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"知识库ID {kb_id} 不存在"))
        
        elif process_all:
            # 处理所有知识库
            kbs = KnowledgeBase.objects.all()
            
            if not kbs.exists():
                self.stdout.write(self.style.WARNING("没有找到知识库"))
                return
            
            self.stdout.write(f"共找到 {kbs.count()} 个知识库")
            
            success_count = 0
            for kb in kbs:
                self.stdout.write(f"正在处理知识库: {kb.name}")
                success = process_knowledge_base(kb.id)
                if success:
                    self.stdout.write(self.style.SUCCESS(f"知识库 {kb.name} 处理完成"))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f"知识库 {kb.name} 处理失败"))
            
            self.stdout.write(self.style.SUCCESS(
                f"处理完成: {success_count}/{kbs.count()} 个知识库成功处理"
            ))
        
        else:
            self.stdout.write(self.style.WARNING("请指定 --id 或 --all 参数")) 