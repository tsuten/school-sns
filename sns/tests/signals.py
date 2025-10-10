from django.dispatch import Signal
from django.dispatch import receiver

test_signal = Signal()
test_signal_2 = Signal()
test_signal_3 = Signal()

@receiver(test_signal)
def test_signal_receiver(sender, user, **kwargs):
    print("test_signal_receiver", user)

@receiver(test_signal_2)
def send_to_user(sender, user, **kwargs):
    from websocket.unified_consumers import send_to_user
    import asyncio
    
    # 非同期関数を同期的に呼び出し
    asyncio.run(send_to_user(
        user_id = user.id,
        message_type = "test", 
        data = {"message": "test_signal_2",
                "tinpo": "うんかすがすぎる"}
    ))

def test_signal_2_signal(message):
    """メッセージ作成シグナルを送信"""
    test_signal_3.send(
        sender=test_signal_2,
        user=message,
    )

@receiver(test_signal_3)
def test_signal_3_receiver(sender, user, **kwargs):
    from websocket.unified_consumers import send_to_user
    import asyncio

    asyncio.run(send_to_user(
        user_id = user.id,
        message_type = "test", 
        data = {"message": "test_signal_3",
                "tinpo": "うんかすがすぎる"}
    ))