from django.core.management.base import BaseCommand
from storage.models import FileCategory


class Command(BaseCommand):
    help = 'Create default file categories for school SNS'

    def handle(self, *args, **options):
        default_categories = [
            {
                'name': 'プリント',
                'slug': 'print',
                'description': '先生から配布されるプリント・教材',
                'icon': '📄',
                'allowed_extensions': ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'],
                'max_file_size': 20971520,  # 20MB
            },
            {
                'name': '課題',
                'slug': 'assignment',
                'description': '生徒が提出する課題・レポート',
                'icon': '📝',
                'allowed_extensions': ['pdf', 'doc', 'docx', 'txt', 'zip'],
                'max_file_size': 10485760,  # 10MB
            },
            {
                'name': '資料',
                'slug': 'material',
                'description': '参考資料・教材・参考書',
                'icon': '📚',
                'allowed_extensions': ['pdf', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx'],
                'max_file_size': 52428800,  # 50MB
            },
            {
                'name': '連絡',
                'slug': 'notice',
                'description': '重要なお知らせ・連絡事項',
                'icon': '📢',
                'allowed_extensions': ['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'],
                'max_file_size': 5242880,  # 5MB
            },
            {
                'name': '画像',
                'slug': 'image',
                'description': '写真・画像ファイル',
                'icon': '🖼️',
                'allowed_extensions': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'],
                'max_file_size': 10485760,  # 10MB
            },
            {
                'name': '動画',
                'slug': 'video',
                'description': '動画ファイル',
                'icon': '🎬',
                'allowed_extensions': ['mp4', 'avi', 'mov', 'wmv', 'webm'],
                'max_file_size': 104857600,  # 100MB
            },
            {
                'name': 'その他',
                'slug': 'other',
                'description': 'その他のファイル',
                'icon': '📁',
                'allowed_extensions': [],  # 全て許可
                'max_file_size': 20971520,  # 20MB
            },
        ]

        for category_data in default_categories:
            category, created = FileCategory.objects.get_or_create(
                slug=category_data['slug'],
                defaults=category_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created default file categories!')
        )