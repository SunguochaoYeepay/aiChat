"""
知识库迁移命令 - 将文件系统知识库迁移到数据库

此脚本用于将knowledge_base目录中的Markdown文件迁移到数据库中。
"""
from django.core.management.base import BaseCommand
from pathlib import Path
from management.models import KnowledgeBase
import os

class Command(BaseCommand):
    help = '将文件系统知识库迁移到数据库'
    
    def handle(self, *args, **options):
        # 获取知识库目录路径
        kb_dir = Path('knowledge_base')
        if not kb_dir.exists():
            self.stdout.write(self.style.ERROR('知识库目录不存在'))
            return
        
        imported_count = 0
        skipped_count = 0
        
        # 遍历目录中的所有Markdown文件
        for md_file in kb_dir.glob('*.md'):
            # 检查文件是否已经导入
            filename = md_file.name
            file_path = str(md_file)
            
            # 如果文件已存在，则跳过
            if KnowledgeBase.objects.filter(file_path=file_path).exists():
                self.stdout.write(f"跳过已导入文件: {filename}")
                skipped_count += 1
                continue
            
            # 读取文件内容
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 创建知识库记录
                name = os.path.splitext(filename)[0]  # 文件名作为知识库名称
                kb = KnowledgeBase(
                    name=name,
                    description=f"{name}知识库文档",
                    file_path=file_path,
                    content=content
                )
                kb.save()
                self.stdout.write(self.style.SUCCESS(f"导入文件: {filename}"))
                imported_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"导入文件{filename}时出错: {str(e)}"))
        
        # 输出导入统计
        self.stdout.write(self.style.SUCCESS(
            f'导入完成: 成功导入{imported_count}个文件，跳过{skipped_count}个已存在文件'
        )) 