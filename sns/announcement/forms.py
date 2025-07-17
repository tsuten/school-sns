from django import forms
from .models import Announcement
from enrollments.models import School, Class

class PostToChoiceField(forms.ChoiceField):
    """学校とクラスを統合したドロップダウンフィールド"""
    
    def __init__(self, *args, **kwargs):
        choices = [('', '配信先を選択してください')]
        
        # 学校の選択肢を追加
        for school in School.objects.all():
            choices.append((f"school_{school.id}", f"学校: {school.name}"))
        
        # クラスの選択肢を追加
        for class_obj in Class.objects.all():
            choices.append((f"class_{class_obj.id}", f"クラス: {class_obj.name}"))
        
        kwargs['choices'] = choices
        super().__init__(*args, **kwargs)

class AnnouncementForm(forms.ModelForm):
    # 統合された配信先選択フィールド
    post_to_selection = PostToChoiceField(
        label="配信先",
        required=True,
        help_text="配信先の学校またはクラスを選択してください"
    )

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'is_pinned']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 編集時の初期値設定
        if self.instance and self.instance.pk and self.instance.post_to:
            try:
                # 学校かクラスかを判定して初期値を設定
                school = School.objects.filter(id=self.instance.post_to).first()
                if school:
                    self.fields['post_to_selection'].initial = f"school_{school.id}"
                else:
                    class_obj = Class.objects.filter(id=self.instance.post_to).first()
                    if class_obj:
                        self.fields['post_to_selection'].initial = f"class_{class_obj.id}"
            except:
                pass

    def clean_post_to_selection(self):
        """post_to_selectionの値を検証し、UUIDを抽出"""
        selection = self.cleaned_data.get('post_to_selection')
        if not selection:
            raise forms.ValidationError('配信先を選択してください。')
        
        try:
            target_type, target_id = selection.split('_', 1)
            if target_type == 'school':
                school = School.objects.get(id=target_id)
                return school.id
            elif target_type == 'class':
                class_obj = Class.objects.get(id=target_id)
                return class_obj.id
            else:
                raise forms.ValidationError('無効な配信先です。')
        except (ValueError, School.DoesNotExist, Class.DoesNotExist):
            raise forms.ValidationError('無効な配信先です。')

    def _post_clean(self):
        """モデルのバリデーションを実行する前にpost_toを設定"""
        # post_to_selectionが正常に処理されている場合は、post_toを事前に設定
        if 'post_to_selection' in self.cleaned_data and not self.errors:
            self.instance.post_to = self.cleaned_data['post_to_selection']
        
        # 通常のフィールドバリデーションを実行（post_toは既に設定済み）
        super()._post_clean()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.post_to = self.cleaned_data['post_to_selection']
        if commit:
            instance.save()
        return instance 