from django.core.management.base import BaseCommand
import os
from pathlib import Path
from management.models import KnowledgeBase, ServiceControl

class Command(BaseCommand):
    help = '导入知识库文档和服务脚本'

    def handle(self, *args, **options):
        self.stdout.write('开始导入资源...')
        
        # 导入知识库文档
        self.import_knowledge_base()
        
        # 导入服务脚本
        self.import_services()
        
        self.stdout.write(self.style.SUCCESS('导入完成!'))
    
    def import_knowledge_base(self):
        """导入知识库文档"""
        self.stdout.write('导入知识库文档...')
        
        # 获取知识库目录路径
        kb_dir = Path('knowledge_base')
        if not kb_dir.exists():
            self.stdout.write(self.style.WARNING('知识库目录不存在，跳过导入'))
            return
        
        imported_count = 0
        # 遍历目录中的所有Markdown文件
        for md_file in kb_dir.glob('*.md'):
            # 检查文件是否已经导入
            filename = md_file.name
            file_path = str(md_file)
            
            # 如果文件已存在，则跳过
            if KnowledgeBase.objects.filter(file_path=file_path).exists():
                continue
            
            # 读取文件内容
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
            imported_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'成功导入{imported_count}个知识库文档'))
    
    def import_services(self):
        """导入服务脚本"""
        self.stdout.write('导入服务脚本...')
        
        # 检查GPU服务脚本
        gpu_script = Path('run_gpu_server.bat')
        if gpu_script.exists():
            # 如果服务已存在，则跳过
            if not ServiceControl.objects.filter(name='GPU图像分析服务').exists():
                ServiceControl.objects.create(
                    name='GPU图像分析服务',
                    description='启动GPU加速的图像分析服务器',
                    status='stopped',
                    command=str(gpu_script.absolute())
                )
                self.stdout.write(self.style.SUCCESS('成功导入GPU服务'))
        else:
            self.stdout.write(self.style.WARNING('GPU服务脚本不存在，跳过导入')) 