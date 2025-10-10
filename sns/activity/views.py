from ninja import Router
from .schemas import ActivitySchema, ActivityFilterSchema
from typing import List
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth import get_user_model
from django.db.models import Q
from datetime import datetime, timedelta

User = get_user_model()
router = Router(tags=['activity'])

def get_user_posts_activities(user, limit: int = 50, offset: int = 0):
    """ユーザーの投稿アクティビティを取得"""
    activities = []
    try:
        from posts.models import Post
        posts = Post.objects.filter(user=user, is_deleted=False).order_by('-created_at')[offset:offset + limit]
        for post in posts:
            try:
                activities.append({
                    'id': str(post.id),
                    'type': 'post_created',
                    'description': f"投稿「{post.title}」を作成しました",
                    'user_id': str(user.id),
                    'username': user.username,
                    'created_at': post.created_at,
                    'metadata': {'post_id': str(post.id), 'title': post.title}
                })
            except Exception as e:
                print(f"Error processing post {post.id}: {e}")
                continue
    except ImportError:
        pass
    except Exception as e:
        print(f"Error getting posts: {e}")
    
    return activities

def get_user_events_activities(user, limit: int = 50, offset: int = 0):
    """ユーザーのイベントアクティビティを取得"""
    activities = []
    try:
        from events.models import Event
        events = Event.objects.filter(user=user, is_deleted=False).order_by('-created_at')[offset:offset + limit]
        for event in events:
            try:
                activities.append({
                    'id': str(event.id),
                    'type': 'event_created',
                    'description': f"イベント「{event.title}」を作成しました",
                    'user_id': str(user.id),
                    'username': user.username,
                    'created_at': event.created_at,
                    'metadata': {'event_id': str(event.id), 'title': event.title}
                })
            except Exception as e:
                print(f"Error processing event {event.id}: {e}")
                continue
    except ImportError:
        pass
    except Exception as e:
        print(f"Error getting events: {e}")
    
    return activities

def get_user_polls_activities(user, limit: int = 50, offset: int = 0):
    """ユーザーの投票アクティビティを取得"""
    activities = []
    try:
        from polls.models import Poll
        polls = Poll.objects.filter(user=user, is_deleted=False).order_by('-created_at')[offset:offset + limit]
        for poll in polls:
            try:
                activities.append({
                    'id': str(poll.id),
                    'type': 'poll_created',
                    'description': f"投票「{poll.title}」を作成しました",
                    'user_id': str(user.id),
                    'username': user.username,
                    'created_at': poll.created_at,
                    'metadata': {'poll_id': str(poll.id), 'title': poll.title}
                })
            except Exception as e:
                print(f"Error processing poll {poll.id}: {e}")
                continue
    except ImportError:
        pass
    except Exception as e:
        print(f"Error getting polls: {e}")
    
    return activities

def get_user_circle_activities(user, limit: int = 50, offset: int = 0):
    """ユーザーのサークル関連アクティビティを取得"""
    activities = []
    try:
        from circle.models import CircleMembership
        memberships = CircleMembership.objects.filter(user=user).order_by('-created_at')[offset:offset + limit]
        for membership in memberships:
            try:
                activities.append({
                    'id': str(membership.id),
                    'type': 'circle_joined',
                    'description': f"サークル「{membership.circle.name}」に参加しました",
                    'user_id': str(user.id),
                    'username': user.username,
                    'created_at': membership.created_at,
                    'metadata': {'circle_id': str(membership.circle.id), 'circle_name': membership.circle.name}
                })
            except Exception as e:
                print(f"Error processing membership {membership.id}: {e}")
                continue
    except ImportError:
        pass
    except Exception as e:
        print(f"Error getting memberships: {e}")
    
    return activities

def get_user_memo_activities(user, limit: int = 50, offset: int = 0):
    """ユーザーのメモアクティビティを取得"""
    activities = []
    try:
        from apps.memo.models import Memo
        memos = Memo.objects.filter(user=user, is_deleted=False).order_by('-created_at')[offset:offset + limit]
        for memo in memos:
            try:
                activities.append({
                    'id': str(memo.id),
                    'type': 'memo_created',
                    'description': f"メモを作成しました",
                    'user_id': str(user.id),
                    'username': user.username,
                    'created_at': memo.created_at,
                    'metadata': {'memo_id': str(memo.id)}
                })
            except Exception as e:
                print(f"Error processing memo {memo.id}: {e}")
                continue
    except ImportError:
        pass
    except Exception as e:
        print(f"Error getting memos: {e}")
    
    return activities

def get_user_assignment_activities(user, limit: int = 50, offset: int = 0):
    """ユーザーの課題アクティビティを取得"""
    activities = []
    try:
        from assignments.models import Assignment
        assignments = Assignment.objects.filter(created_by=user, is_deleted=False).order_by('-created_at')[offset:offset + limit]
        for assignment in assignments:
            try:
                activities.append({
                    'id': str(assignment.id),
                    'type': 'assignment_created',
                    'description': f"課題「{assignment.title}」を作成しました",
                    'user_id': str(user.id),
                    'username': user.username,
                    'created_at': assignment.created_at,
                    'metadata': {'assignment_id': str(assignment.id), 'title': assignment.title}
                })
            except Exception as e:
                print(f"Error processing assignment {assignment.id}: {e}")
                continue
    except ImportError:
        pass
    except Exception as e:
        print(f"Error getting assignments: {e}")
    
    return activities

def get_user_activities(user_id: str, limit: int = 50, offset: int = 0):
    """指定されたユーザーのアクティビティを取得"""
    try:
        user = User.objects.get(id=user_id)
        activities = []
        
        # 各タイプのアクティビティを取得
        activities.extend(get_user_posts_activities(user, limit, offset))
        activities.extend(get_user_events_activities(user, limit, offset))
        activities.extend(get_user_polls_activities(user, limit, offset))
        activities.extend(get_user_circle_activities(user, limit, offset))
        activities.extend(get_user_memo_activities(user, limit, offset))
        activities.extend(get_user_assignment_activities(user, limit, offset))
        
        # 作成日時でソート
        try:
            activities.sort(key=lambda x: x['created_at'], reverse=True)
        except Exception as e:
            print(f"Error sorting activities: {e}")
        
        return activities[offset:offset + limit]
        
    except User.DoesNotExist:
        return []
    except Exception as e:
        print(f"Error in get_user_activities: {e}")
        return []

def get_feed_activities(user, limit: int = 50, offset: int = 0):
    """ユーザーのフィードアクティビティを取得"""
    try:
        if not user:
            return []
            
        activities = []
        
        # 自分のアクティビティ
        try:
            own_activities = get_user_activities(str(user.id), limit=limit, offset=0)
            activities.extend(own_activities)
        except Exception as e:
            print(f"Error getting own activities: {e}")
        
        # フォローしているユーザーのアクティビティ
        try:
            from relations.models import Follow
            following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
            
            for following_user_id in following_users[:10]:  # 最大10ユーザー分
                try:
                    following_activities = get_user_activities(str(following_user_id), limit=20, offset=0)
                    activities.extend(following_activities)
                except Exception as e:
                    print(f"Error getting following user activities: {e}")
                    continue
        except ImportError:
            pass
        except Exception as e:
            print(f"Error getting following users: {e}")
        
        # 所属サークルのアクティビティ
        try:
            from circle.models import CircleMembership
            memberships = CircleMembership.objects.filter(user=user).values_list('circle', flat=True)
            
            for circle_id in memberships[:5]:  # 最大5サークル分
                try:
                    from circle.models import Circle
                    circle = Circle.objects.get(id=circle_id)
                    circle_activities = get_user_activities(str(circle.owner.id), limit=10, offset=0)
                    activities.extend(circle_activities)
                except Exception as e:
                    print(f"Error getting circle activities: {e}")
                    continue
        except ImportError:
            pass
        except Exception as e:
            print(f"Error getting circle memberships: {e}")
        
        # 作成日時でソート
        try:
            activities.sort(key=lambda x: x['created_at'], reverse=True)
        except Exception as e:
            print(f"Error sorting activities: {e}")
        
        return activities[offset:offset + limit]
    except Exception as e:
        print(f"Error in get_feed_activities: {e}")
        return []

@router.get('/user/{user_id}', response=List[ActivitySchema])
def get_user_activities_api(request, user_id: str, limit: int = 50, offset: int = 0):
    """指定されたユーザーのアクティビティを取得"""
    activities = get_user_activities(user_id, limit, offset)
    return activities

@router.get('/feed', response=List[ActivitySchema], auth=JWTAuth())
def get_feed_activities_api(request, limit: int = 50, offset: int = 0):
    """認証済みユーザーのフィードアクティビティを取得"""
    try:
        if not request.auth:
            return []
        
        activities = get_feed_activities(request.auth, limit, offset)
        return activities
    except Exception as e:
        print(f"Error in get_feed_activities_api: {e}")
        return []

@router.get('/filter', response=List[ActivitySchema])
def filter_activities(request, filters: ActivityFilterSchema):
    """フィルタリング条件に基づいてアクティビティを取得"""
    activities = []
    
    if filters.user_id:
        # 特定ユーザーのアクティビティ
        activities = get_user_activities(filters.user_id, filters.limit, filters.offset)
    else:
        # 全ユーザーのアクティビティ（認証が必要）
        if hasattr(request, 'auth') and request.auth:
            activities = get_feed_activities(request.auth, filters.limit, filters.offset)
    
    # アクティビティタイプでフィルタリング
    if filters.activity_type:
        activities = [a for a in activities if a['type'] == filters.activity_type]
    
    # 日付範囲でフィルタリング
    if filters.start_date:
        activities = [a for a in activities if a['created_at'] >= filters.start_date]
    if filters.end_date:
        activities = [a for a in activities if a['created_at'] <= filters.end_date]
    
    return activities

@router.get('/summary/{user_id}')
def get_user_activity_summary(request, user_id: str):
    """ユーザーのアクティビティサマリーを取得"""
    try:
        user = User.objects.get(id=user_id)
        activities = get_user_activities(user_id, limit=1000, offset=0)
        
        # タイプ別の集計
        type_counts = {}
        for activity in activities:
            activity_type = activity['type']
            type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
        
        # 最近のアクティビティ
        recent_activities = activities[:10]
        
        return {
            'user_id': str(user.id),
            'username': user.username,
            'total_activities': len(activities),
            'type_counts': type_counts,
            'recent_activities': recent_activities,
            'last_activity': activities[0]['created_at'] if activities else None
        }
        
    except User.DoesNotExist:
        return {"error": "User not found"}
