def get():
    """ ユーザー情報を取得する """
    return {"message": "Hello, World!"}

def post(request):
    """ ニガースを取得する """
    # Django Ninjaでは request.body または request.POST を使用
    try:
        # リクエストボディを取得
        import json
        body = request.body.decode('utf-8')
        if body:
            data = json.loads(body)
            if data.get('name'):
                return {"message": "Hello, {}!".format(data.get('name'))}
        
        return {"message": "Hello, World!"}
    except Exception as e:
        return {"message": "Hello, World!", "error": str(e)} 