from ninja import Router
from ninja_jwt.authentication import JWTAuth
from .signals import test_signal_2
router = Router(tags=['tests'])

@router.get('/test', auth=JWTAuth())
def test(request):
    return {"message": "Hello, World!"}

@router.get("/get-signal", auth=JWTAuth())
def get_signal(request):
    test_signal_2.send(sender=None, user=request.user)
    return {"message": "Signal sent"}