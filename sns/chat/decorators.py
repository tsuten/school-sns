from shared.decorators import send_signal

def send_message_signal(signal_type):
    """
    メッセージ専用シグナル送信デコレーター
    
    Args:
        signal_type (str): シグナルの種類 ('post', 'update', 'delete', 'restore')
    """
    return send_signal(
        signal_type=signal_type,
        signal_module_path='chat.signals',
        model_class=None,  # 動的に取得するためNoneに設定
        signal_mapping={
            'post': 'message_post_signal',
            'update': 'message_update_signal',
            'delete': 'message_delete_signal',
            'restore': 'message_restore_signal'
        }
    ) 