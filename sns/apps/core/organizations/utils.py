from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q
from django.apps import apps
from typing import Optional, Union, List, Dict, Any, Type
from .models import Class, School, AbstractOrganization, OrganizationType
import inspect


class OrganizationManagerService:
    """
    組織管理のためのサービスクラス
    AbstractOrganizationのメソッドを効率的に呼び出すための統一インターフェース
    動的な組織管理機能を提供
    """
    
    # 動的モデルレジストリ（高度な機能用：cross_organization_analysis等）
    # 基本的な組織検出・取得はmodels.pyのOrganizationManagerを使用
    _organization_registry: Dict[str, Type[AbstractOrganization]] = {}
    
    @classmethod
    def register_organization_model(cls, org_type: str, model_class: Type[AbstractOrganization]):
        """組織モデルを動的に登録（高度な機能用）"""
        cls._organization_registry[org_type] = model_class
    
    @classmethod
    def get_registered_models(cls) -> Dict[str, Type[AbstractOrganization]]:
        """登録済みモデルを取得（複数組織分析用）"""
        if not cls._organization_registry:
            # デフォルト登録
            cls.register_organization_model(OrganizationType.CLASS, Class)
            cls.register_organization_model(OrganizationType.SCHOOL, School)
        return cls._organization_registry
    
    @classmethod
    def auto_detect_organization_type(cls, organization_id: str) -> Optional[str]:
        """組織IDから組織タイプを検出（models.pyのメソッドを呼び出し）"""
        from .models import Organization
        
        try:
            return Organization.objects.get_organization_type_by_id(organization_id)
        except ValidationError:
            return None
    
    @classmethod
    def get_organization_by_id_explicit(cls, organization_id: str, org_type: Optional[str] = None) -> AbstractOrganization:
        """組織インスタンスを取得（models.pyのメソッドを呼び出し）"""
        from .models import Organization
        
        return Organization.objects.get_organization_by_id(organization_id, org_type)
    
    @classmethod
    def execute_organization_method(cls, organization_id: str, method_name: str, 
                                  *args, org_type: Optional[str] = None, **kwargs) -> Any:
        """組織のメソッドを実行（明示的な分岐処理を使用）"""
        try:
            organization = cls.get_organization_by_id_explicit(organization_id, org_type)
            
            if not hasattr(organization, method_name):
                raise ValidationError(f"Method '{method_name}' not found on {organization.__class__.__name__}")
            
            method = getattr(organization, method_name)
            
            # メソッドが呼び出し可能かチェック
            if not callable(method):
                raise ValidationError(f"'{method_name}' is not a callable method")
            
            return method(*args, **kwargs)
            
        except Exception as e:
            raise ValidationError(f"Error executing method '{method_name}': {str(e)}")
    
    @classmethod
    def batch_execute_methods(cls, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """複数の組織操作をバッチで実行"""
        results = []
        
        for operation in operations:
            try:
                org_id = operation['organization_id']
                method_name = operation['method']
                args = operation.get('args', [])
                kwargs = operation.get('kwargs', {})
                org_type = operation.get('org_type')
                
                result = cls.execute_organization_method(
                    org_id, method_name, *args, org_type=org_type, **kwargs
                )
                
                results.append({
                    'success': True,
                    'organization_id': org_id,
                    'method': method_name,
                    'result': result
                })
                
            except Exception as e:
                results.append({
                    'success': False,
                    'organization_id': operation.get('organization_id'),
                    'method': operation.get('method'),
                    'error': str(e)
                })
        
        return results
    
    @classmethod
    def get_available_methods(cls, organization_id: str, org_type: Optional[str] = None) -> List[str]:
        """組織で利用可能なメソッド一覧を取得"""
        try:
            organization = cls.get_organization_by_id_explicit(organization_id, org_type)
            
            # AbstractOrganizationクラスのメソッドを取得
            methods = []
            
            # 除外するメソッド名（Django内部メソッドとモデル固有メソッド）
            excluded_names = {
                'objects', 'DoesNotExist', 'MultipleObjectsReturned', 
                'save', 'delete', 'clean', 'clean_fields', 'full_clean',
                'refresh_from_db', 'serializable_value', 'get_deferred_fields',
                'Meta', 'check', 'adelete', 'asave', 'arefresh_from_db',
                'date_error_message', 'delete_object', 'restore_object',
                'from_db', 'get_constraints', 'prepare_database_save',
                'save_base', 'unique_error_message', 'validate_constraints',
                'validate_unique', 'get_school_by_class'  # モデル固有メソッド
            }
            
            # Django自動生成メソッドのパターン
            excluded_patterns = [
                'get_next_by_', 'get_previous_by_'
            ]
            
            for name in dir(organization):
                # 基本的な除外条件
                if (name.startswith('_') or 
                    name in excluded_names or
                    name.endswith('_set')):  # リレーションのreverse accessorを除外
                    continue
                
                # パターンマッチによる除外
                should_exclude = False
                for pattern in excluded_patterns:
                    if name.startswith(pattern):
                        should_exclude = True
                        break
                
                if should_exclude:
                    continue
                
                try:
                    attr = getattr(organization, name)
                    
                    # Managerやその他のDjangoの内部属性をスキップ
                    if hasattr(attr, '__class__') and 'Manager' in str(attr.__class__):
                        continue
                        
                    if callable(attr):
                        # メソッドのシグネチャを取得
                        try:
                            sig = inspect.signature(attr)
                            methods.append({
                                'name': name,
                                'signature': str(sig),
                                'doc': attr.__doc__ or 'No documentation'
                            })
                        except (ValueError, TypeError):
                            methods.append({
                                'name': name,
                                'signature': 'N/A',
                                'doc': 'No documentation'
                            })
                except Exception:
                    # アクセスできない属性はスキップ
                    continue
            
            return methods
            
        except Exception as e:
            raise ValidationError(f"Error getting available methods: {str(e)}")
    
    @classmethod
    def smart_member_operation(cls, organization_id: str, user_id: str, operation: str, 
                             role: Optional[str] = None, org_type: Optional[str] = None) -> bool:
        """スマートなメンバー操作（動的メソッド選択）"""
        try:
            from apps.core.users.models import User
            user = User.objects.get(id=user_id)
            
            # 操作に応じて動的にメソッドを選択
            method_mapping = {
                'add': f'add_{role}' if role else 'add_member',
                'remove': f'remove_{role}' if role else 'remove_member', 
                'check_membership': 'is_member',
                'check_manager': 'is_manager',
                'get_role': 'get_user_role'
            }
            
            if operation not in method_mapping:
                raise ValidationError(f"Unknown operation: {operation}")
            
            method_name = method_mapping[operation]
            
            if operation in ['check_membership', 'check_manager', 'get_role']:
                return cls.execute_organization_method(organization_id, method_name, user, org_type=org_type)
            else:
                cls.execute_organization_method(organization_id, method_name, user, org_type=org_type)
                return True
                
        except Exception as e:
            raise ValidationError(f"Error in smart member operation: {str(e)}")
    
    @classmethod
    def cross_organization_analysis(cls, user_id: str) -> Dict[str, Any]:
        """複数組織をまたいだユーザー分析"""
        try:
            from apps.core.users.models import User
            user = User.objects.get(id=user_id)
            
            models_registry = cls.get_registered_models()
            analysis = {
                'user_id': user_id,
                'total_organizations': 0,
                'organizations_by_type': {},
                'roles_summary': {'manager': 0, 'member': 0},
                'detailed_info': []
            }
            
            for org_type, model_class in models_registry.items():
                # 管理している組織
                managed_orgs = model_class.objects.filter(managers=user)
                # メンバーとして所属している組織
                member_orgs = model_class.objects.filter(members=user)
                
                org_info = {
                    'type': org_type,
                    'managed_count': managed_orgs.count(),
                    'member_count': member_orgs.count(),
                    'organizations': []
                }
                
                # 詳細情報を収集
                for org in managed_orgs:
                    org_info['organizations'].append({
                        'id': str(org.id),
                        'name': org.name,
                        'role': 'manager',
                        'members_count': org.get_members_count(),
                        'managers_count': org.get_managers_count()
                    })
                    analysis['roles_summary']['manager'] += 1
                
                for org in member_orgs:
                    if not managed_orgs.filter(id=org.id).exists():  # 重複を避ける
                        org_info['organizations'].append({
                            'id': str(org.id),
                            'name': org.name,
                            'role': 'member',
                            'members_count': org.get_members_count(),
                            'managers_count': org.get_managers_count()
                        })
                        analysis['roles_summary']['member'] += 1
                
                analysis['organizations_by_type'][org_type] = org_info
                analysis['total_organizations'] += len(org_info['organizations'])
            
            return analysis
            
        except Exception as e:
            raise ValidationError(f"Error in cross-organization analysis: {str(e)}")
    
    @staticmethod
    def get_organization_by_id(organization_id: str, org_type: Optional[str] = None) -> AbstractOrganization:
        """
        IDから組織を取得（明示的な分岐処理）
        
        Args:
            organization_id: 組織ID
            org_type: 組織タイプ（'class' or 'school'）。指定しない場合は自動判定
            
        Returns:
            AbstractOrganization: 組織インスタンス
            
        Raises:
            ValidationError: 組織が見つからない場合
        """
        return OrganizationManagerService.get_organization_by_id_explicit(organization_id, org_type)
    
    @staticmethod
    def get_members_with_role_info(organization_id: str, org_type: Optional[str] = None) -> dict:
        """組織のメンバーと役割情報を取得"""
        from apps.core.users.models import User
        
        organization = OrganizationManagerService.get_organization_by_id(organization_id, org_type)
        
        members = organization.members.all()
        managers = organization.managers.all()
        
        members_info = []
        for member in members:
            role = 'manager' if member in managers else 'member'
            members_info.append({
                'user_id': str(member.id),
                'username': member.username,
                'role': role
            })
        
        return {
            'organization_id': organization_id,
            'members': members_info,
            'total_members': len(members_info)
        }
    
    @staticmethod
    def get_user_organizations_with_role(user_id: str) -> dict:
        """
        ユーザーが所属する全組織を役割付きで取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            dict: 組織情報（クラス、学校、役割含む）
        """
        from apps.core.users.models import User
        
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            raise ValidationError(f"User with id {user_id} not found")
        
        # クラス情報を取得
        managed_classes = Class.objects.filter(managers=user)
        member_classes = Class.objects.filter(members=user)
        
        # 学校情報を取得
        managed_schools = School.objects.filter(managers=user)
        member_schools = School.objects.filter(members=user)
        
        return {
            'classes': {
                'managed': [
                    {
                        'organization': cls,
                        'role': 'manager',
                        'members_count': cls.get_members_count(),
                        'managers_count': cls.get_managers_count()
                    } for cls in managed_classes
                ],
                'member': [
                    {
                        'organization': cls,
                        'role': 'member',
                        'members_count': cls.get_members_count(),
                        'managers_count': cls.get_managers_count()
                    } for cls in member_classes if cls not in managed_classes
                ]
            },
            'schools': {
                'managed': [
                    {
                        'organization': school,
                        'role': 'manager',
                        'members_count': school.get_members_count(),
                        'managers_count': school.get_managers_count()
                    } for school in managed_schools
                ],
                'member': [
                    {
                        'organization': school,
                        'role': 'member',
                        'members_count': school.get_members_count(),
                        'managers_count': school.get_managers_count()
                    } for school in member_schools if school not in managed_schools
                ]
            }
        }
    
    @staticmethod
    def add_user_to_organization(organization_id: str, user_id: str, role: str = 'member', 
                                org_type: Optional[str] = None) -> bool:
        """
        組織にユーザーを追加（動的処理でAbstractOrganizationメソッド使用）
        
        Args:
            organization_id: 組織ID
            user_id: ユーザーID
            role: 役割（'manager' or 'member'）
            org_type: 組織タイプ
            
        Returns:
            bool: 追加の成功/失敗
        """
        from apps.core.users.models import User
        
        try:
            org = OrganizationManagerService.get_organization_by_id_explicit(organization_id, org_type)
            user = User.objects.get(id=user_id)
            
            if role == 'manager':
                org.add_manager(user)
            elif role == 'member':
                org.add_member(user)
            else:
                return False
            
            return True
            
        except (ObjectDoesNotExist, ValidationError):
            return False
    
    @staticmethod
    def remove_user_from_organization(organization_id: str, user_id: str, role: Optional[str] = None,
                                     org_type: Optional[str] = None) -> bool:
        """
        組織からユーザーを削除（動的処理でAbstractOrganizationメソッド使用）
        
        Args:
            organization_id: 組織ID
            user_id: ユーザーID
            role: 役割（指定しない場合は両方から削除）
            org_type: 組織タイプ
            
        Returns:
            bool: 削除の成功/失敗
        """
        from apps.core.users.models import User
        
        try:
            org = OrganizationManagerService.get_organization_by_id_explicit(organization_id, org_type)
            user = User.objects.get(id=user_id)
            
            if role == 'manager' or role is None:
                if org.is_manager(user):
                    org.remove_manager(user)
            
            if role == 'member' or role is None:
                if org.is_member(user):
                    org.remove_member(user)
            
            return True
            
        except (ObjectDoesNotExist, ValidationError):
            return False
    
    @staticmethod
    def change_user_role(organization_id: str, user_id: str, new_role: str,
                        org_type: Optional[str] = None) -> bool:
        """
        ユーザーの役割を変更（動的処理でAbstractOrganizationメソッド使用）
        
        Args:
            organization_id: 組織ID
            user_id: ユーザーID
            new_role: 新しい役割（'manager' or 'member'）
            org_type: 組織タイプ
            
        Returns:
            bool: 変更の成功/失敗
        """
        from apps.core.users.models import User
        
        try:
            org = OrganizationManagerService.get_organization_by_id_explicit(organization_id, org_type)
            user = User.objects.get(id=user_id)
            
            # 現在の役割を確認
            current_role = org.get_user_role(user)
            
            if current_role == 'none':
                # ユーザーが組織に所属していない場合は追加
                return OrganizationManagerService.add_user_to_organization(
                    organization_id, user_id, new_role, org_type
                )
            
            if current_role != new_role:
                # 現在の役割から削除
                if current_role == 'manager':
                    org.remove_manager(user)
                elif current_role == 'member':
                    org.remove_member(user)
                
                # 新しい役割に追加
                if new_role == 'manager':
                    org.add_manager(user)
                elif new_role == 'member':
                    org.add_member(user)
            
            return True
            
        except (ObjectDoesNotExist, ValidationError):
            return False
    
    @staticmethod
    def get_organization_stats(organization_id: str, org_type: Optional[str] = None) -> dict:
        """
        組織の統計情報を取得（動的処理でAbstractOrganizationメソッド使用）
        
        Args:
            organization_id: 組織ID
            org_type: 組織タイプ
            
        Returns:
            dict: 統計情報
        """
        try:
            org = OrganizationManagerService.get_organization_by_id_explicit(organization_id, org_type)
            detected_org_type = org_type or OrganizationManagerService.auto_detect_organization_type(organization_id)
            
            return {
                'id': str(org.id),
                'name': org.name,
                'type': detected_org_type,
                'managers_count': org.get_managers_count(),
                'members_count': org.get_members_count(),
                'total_users': org.get_managers_count() + org.get_members_count(),
                'created_at': org.created_at,
                'updated_at': org.updated_at
            }
            
        except (ObjectDoesNotExist, ValidationError):
            return {}
    
    @staticmethod
    def search_organizations_by_user_permission(user_id: str, permission_level: str = 'member') -> List[AbstractOrganization]:
        """
        ユーザーの権限レベルに基づいて組織を検索
        
        Args:
            user_id: ユーザーID
            permission_level: 権限レベル（'manager', 'member', 'any'）
            
        Returns:
            List[AbstractOrganization]: 組織リスト
        """
        from apps.core.users.models import User
        
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return []
        
        organizations = []
        
        if permission_level in ['manager', 'any']:
            # 管理している組織
            organizations.extend(Class.objects.filter(managers=user))
            organizations.extend(School.objects.filter(managers=user))
        
        if permission_level in ['member', 'any']:
            # メンバーとして所属している組織
            organizations.extend(Class.objects.filter(members=user))
            organizations.extend(School.objects.filter(members=user))
        
        # 重複を除去して返す
        return list(set(organizations))
