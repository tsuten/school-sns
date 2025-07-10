from django import forms
from .models import Announcement, School, Class

class AnnouncementForm(forms.ModelForm):
    # 配信先の種類を選択するラジオボタン
    post_to_type = forms.ChoiceField(
        choices=[('school', '学校全体'), ('class', 'クラス単位')],
        widget=forms.RadioSelect,
        label="配信先の種類",
        required=True
    )

    # 配信先の学校を選択するドロップダウン
    target_school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        label="対象の学校",
        required=False
    )

    # 配信先のクラスを選択するドロップダウン
    target_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        label="対象のクラス",
        required=False
    )

    class Meta:
        model = Announcement
        # posted_by を除外。これは管理画面側で自動設定します。
        fields = ['title', 'content', 'priority', 'is_pinned']
    
    class Media:
        js = ('announcement/admin.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.posted_to_school.exists():
                self.fields['post_to_type'].initial = 'school'
                self.fields['target_school'].initial = self.instance.posted_to_school.first()
            elif self.instance.posted_to_class.exists():
                self.fields['post_to_type'].initial = 'class'
                self.fields['target_class'].initial = self.instance.posted_to_class.first()

    def clean(self):
        cleaned_data = super().clean()
        post_type = cleaned_data.get('post_to_type')
        school = cleaned_data.get('target_school')
        class_ = cleaned_data.get('target_class')

        if post_type == 'school' and not school:
            self.add_error('target_school', '学校を選択してください。')
        elif post_type == 'class' and not class_:
            self.add_error('target_class', 'クラスを選択してください。')
        
        return cleaned_data 