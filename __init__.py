import os
import datetime
from settings import Config
from app.authentication.handlers import handle_admin_required
from flask import redirect, request, url_for, render_template
from app.core.main.BasePlugin import BasePlugin
from app.core.main.ObjectsStorage import objects

class Storage(BasePlugin):

    def __init__(self,app):
        super().__init__(app,__name__)
        self.title = "Storage"
        self.description = """File manager for storage"""
    
    def initialization(self):
        os.makedirs(Config.FILES_DIR, exist_ok=True)

    def admin(self, request):
        op = request.args.get("op", None)
        path = request.args.get("path","")

        if op == 'create_dir':
            new_dir = request.form['new_dir']
            current_path = request.form['current_path']
            full_path = os.path.join(Config.FILES_DIR, current_path, new_dir)
            os.makedirs(full_path, exist_ok=True)
            return redirect("Storage?path=" + current_path)
        elif op == 'delete_dir':
            dir_to_delete = request.form['dir_to_delete']
            current_path = request.form['current_path']
            full_path = os.path.join(Config.FILES_DIR, current_path, dir_to_delete)
            os.rmdir(full_path)
            return redirect("Storage?path=" + current_path)
        elif op == 'upload':
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            current_path = request.form['current_path']
            if file.filename != '':
                file.save(os.path.join(Config.FILES_DIR, current_path, file.filename))
            return redirect('Storage?path=' + current_path)
        elif op == 'delete_file':
            file_to_delete = request.form['file_to_delete']
            current_path = request.form['current_path']
            full_path = os.path.join(Config.FILES_DIR, current_path, file_to_delete)
            os.remove(full_path)
            return redirect('Storage?path=' + current_path)
        elif op == 'view_file':
            full_path = os.path.join(Config.FILES_DIR, path)
            with open(full_path, 'r') as f:
                content = f.read()
            return render_template('file_view.html', content=content)
        
        full_path = os.path.join(Config.FILES_DIR, path)
        if not os.path.exists(full_path):
            return "Directory not found", 404
            
        items = self.list_files_and_dirs(path)
        return render_template('storage_main.html', items=items, current_path=path)
    
    def list_files_and_dirs(self, path):
        IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"}
        items = []
        full_path = os.path.join(Config.FILES_DIR, path)
        with os.scandir(full_path) as it:
            for entry in it:
                is_pic = '.' in entry.name and entry.name.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS
                items.append(
                    {
                        'name': entry.name,
                        'path': os.path.join(path, entry.name),
                        'is_dir': entry.is_dir(),
                        'is_pic': is_pic,
                        'size': entry.stat().st_size,
                        'dt': datetime.datetime.fromtimestamp(entry.stat().st_atime),
                    }
                )
        return items
