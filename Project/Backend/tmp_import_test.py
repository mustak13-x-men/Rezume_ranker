import importlib.util, sys
spec = importlib.util.spec_from_file_location('app','project/app.py')
app = importlib.util.module_from_spec(spec)
sys.modules['app'] = app
spec.loader.exec_module(app)
print('import successful')
