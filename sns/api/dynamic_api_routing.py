import os
import importlib.util
import glob
import json

class DynamicAPIRouting:
    def __init__(self):
        # Djangoの設定が読み込まれた後にninjaをインポート
        from ninja import Router
        self.router = Router()
        self.discovered_routes = {}

    @classmethod
    def get_router(cls):
        """クラスメソッドでルーターを取得し、ルートを自動読み込み"""
        instance = cls()
        instance.load_routes()
        return instance.router

    def register_router(self, router):
        """ルーターを登録する"""
        self.router.add_router(router)

    def load_routes(self):
        """APIディレクトリ内のルートファイルを動的に読み込む"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"探索開始ディレクトリ: {current_dir}")
        
        # 再帰的にディレクトリを探索
        self._explore_directory(current_dir, "api")
    
    def _explore_directory(self, dir_path, module_prefix):
        """ディレクトリを再帰的に探索する"""
        print(f"ディレクトリ探索中: {dir_path} (プレフィックス: {module_prefix})")
        
        try:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                
                if os.path.isdir(item_path):
                    print(f"  サブディレクトリ発見: {item}")
                    # サブディレクトリを再帰的に探索
                    new_prefix = f"{module_prefix}.{item}"
                    self._explore_directory(item_path, new_prefix)
                elif item.endswith('.py') and not item.endswith('__init__.py') and module_prefix != "api":
                    # apiフォルダ内のファイルはスキャンしない
                    print(f"  Pythonファイル発見: {item}")
                    self._process_python_file(item_path, module_prefix, item)
                    
        except Exception as e:
            print(f"  ディレクトリ探索エラー: {e}")
    
    def _process_python_file(self, file_path, module_prefix, filename):
        """Pythonファイルを処理する"""
        try:
            # ファイル名からモジュール名を生成
            module_name = f"{module_prefix}.{os.path.splitext(filename)[0]}"
            print(f"    モジュール名: {module_name}")
            
            # HTTPメソッド名のリスト
            http_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
            
            # ファイルの内容を確認してHTTPメソッド関数とdocstringを検索
            http_functions = []
            function_details = []
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        if line.startswith('def '):
                            # 関数定義から関数名を抽出
                            func_name = line.split('(')[0].replace('def ', '').strip()
                            
                            # docstringを取得
                            docstring = ""
                            j = i + 1
                            while j < len(lines):
                                next_line = lines[j].strip()
                                if next_line.startswith('"""') or next_line.startswith("'''"):
                                    # docstringの開始
                                    quote_char = next_line[:3] if next_line.startswith('"""') else next_line[:3]
                                    docstring_start = j
                                    
                                    # 同じ行にdocstringの終了があるかチェック
                                    if next_line.endswith(quote_char) and len(next_line) > 3:
                                        # 同じ行でdocstringが完結
                                        docstring = next_line[3:-3].strip()  # 三重引用符を除去
                                    else:
                                        # 複数行のdocstring
                                        j += 1
                                        while j < len(lines):
                                            if lines[j].strip().endswith(quote_char):
                                                # docstringの終了
                                                docstring_lines = lines[docstring_start:j+1]
                                                # 最初と最後の行から三重引用符を除去
                                                if len(docstring_lines) > 0:
                                                    first_line = docstring_lines[0][3:]  # 最初の行から開始の三重引用符を除去
                                                    last_line = docstring_lines[-1][:-3]  # 最後の行から終了の三重引用符を除去
                                                    docstring_lines[0] = first_line
                                                    docstring_lines[-1] = last_line
                                                docstring = '\n'.join(docstring_lines).strip()
                                                break
                                            j += 1
                                    break
                                elif next_line and not next_line.startswith('#'):
                                    # 空行やコメント以外の行が来たらdocstringはない
                                    break
                                j += 1
                            
                            # 関数情報を保存
                            func_info = {
                                'name': func_name,
                                'docstring': docstring
                            }
                            function_details.append(func_info)
                            
                            # HTTPメソッド関数かチェック
                            if func_name.lower() in http_methods:
                                http_functions.append(func_name)
                        
                        i += 1
                        
            except Exception as e:
                print(f"    ファイル読み込みエラー: {e}")
            
            # 階層構造を作成
            self._build_hierarchical_structure(file_path, module_prefix, filename, http_functions, function_details)
            
        except Exception as e:
            print(f"    ファイル処理エラー: {e}")
    
    def _build_hierarchical_structure(self, file_path, module_prefix, filename, http_functions, function_details):
        """階層構造を作成する"""
        # モジュールプレフィックスを分割
        parts = module_prefix.split('.')
        
        # apiディレクトリを起点として階層構造を作成
        current_level = self.discovered_routes
        
        # apiレベル
        if 'api' not in current_level:
            current_level['api'] = {}
        current_level = current_level['api']
        
        # v1, v2などのバージョンレベル
        if len(parts) > 1:
            version = parts[1]
            if version not in current_level:
                current_level[version] = {}
            current_level = current_level[version]
            
            # auth, messagesなどの機能レベル
            if len(parts) > 2:
                feature = parts[2]
                if feature not in current_level:
                    current_level[feature] = {}
                current_level = current_level[feature]
                
                # ファイルレベル（拡張子なし）
                file_base = os.path.splitext(filename)[0]
                if file_base not in current_level:
                    current_level[file_base] = {}
                
                # HTTPメソッドとdocstringを保存
                for func_info in function_details:
                    if func_info['name'].lower() in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                        method_key = f"@{func_info['name'].lower()}"
                        current_level[file_base][method_key] = func_info['docstring']
                        
                        # ルーターに直接登録
                        self._register_to_router(parts, file_path, file_base, func_info)
    
    def _register_to_router(self, parts, file_path, file_base, func_info):
        """ルーターに直接登録する"""
        try:
            # パスを構築
            if len(parts) >= 3:
                # api/v1/auth/get-user のようなパスを構築
                # apiとv1を除いて、auth/get-userのみを使用
                path_parts = parts[2:]  # apiとv1を除く
                path_parts.append(file_base)
                route_path = "/" + "/".join(path_parts)
                
                # タグを決定（機能レベルのフォルダ名）
                tag = parts[2] if len(parts) > 2 else "default"
                
                # HTTPメソッドを取得
                http_method = func_info['name'].lower()
                
                # ファイルから実際の関数を読み込んで実行する関数を作成
                def create_endpoint_function(file_path, func_name, docstring):
                    def endpoint_function(request):
                        try:
                            # ファイルを動的に読み込んで関数を実行
                            import importlib.util
                            spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # 関数を取得して実行
                            if hasattr(module, func_name):
                                func = getattr(module, func_name)
                                return func(request)  # requestパラメータを渡す
                            else:
                                return {"error": f"Function {func_name} not found"}
                        except Exception as e:
                            return {"error": f"Error executing function: {str(e)}"}
                    
                    endpoint_function.__name__ = file_base
                    endpoint_function.__doc__ = docstring
                    return endpoint_function
                
                # ルーターに登録（タグ付き）
                if http_method == 'get':
                    self.router.get(route_path, tags=[tag])(create_endpoint_function(file_path, func_info['name'], func_info['docstring']))
                elif http_method == 'post':
                    self.router.post(route_path, tags=[tag])(create_endpoint_function(file_path, func_info['name'], func_info['docstring']))
                elif http_method == 'put':
                    self.router.put(route_path, tags=[tag])(create_endpoint_function(file_path, func_info['name'], func_info['docstring']))
                elif http_method == 'patch':
                    self.router.patch(route_path, tags=[tag])(create_endpoint_function(file_path, func_info['name'], func_info['docstring']))
                elif http_method == 'delete':
                    self.router.delete(route_path, tags=[tag])(create_endpoint_function(file_path, func_info['name'], func_info['docstring']))
                elif http_method == 'head':
                    self.router.head(route_path, tags=[tag])(create_endpoint_function(file_path, func_info['name'], func_info['docstring']))
                elif http_method == 'options':
                    self.router.options(route_path, tags=[tag])(create_endpoint_function(file_path, func_info['name'], func_info['docstring']))
                
                print(f"    ルーターに登録: {http_method.upper()} {route_path} (タグ: {tag})")
                
        except Exception as e:
            print(f"    ルーター登録エラー: {e}")

    def get_route_list(self):
        """発見されたルートの一覧を取得する"""
        return self.discovered_routes

    def print_routes_json(self):
        """発見されたルートをJSON形式で表示する"""
        import json
        print(json.dumps(self.discovered_routes, indent=2, ensure_ascii=False, default=str))

if __name__ == '__main__':
    routing = DynamicAPIRouting()
    routing.load_routes()
    routing.print_routes_json()