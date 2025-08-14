from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from sentence_transformers import SentenceTransformer, util
import faiss
import json
import os
from flask_cors import CORS
import re
import numpy as np
import requests
from werkzeug.utils import secure_filename
import uuid
import threading
import time
from typing import List, Dict, Any, Optional, Union


app = Flask(__name__)
CORS(app)

# 文件锁字典，用于防止并发写入冲突
file_locks = {}
lock_dict_mutex = threading.Lock()

# 用户会话管理
active_users = set()
user_activity_lock = threading.Lock()

def register_user_activity(username: str) -> None:
    """注册用户活动"""
    with user_activity_lock:
        active_users.add(username)

def get_active_users_count() -> int:
    """获取当前活跃用户数"""
    with user_activity_lock:
        return len(active_users)

def get_file_lock(file_path: str):
    """获取文件锁，确保线程安全"""
    with lock_dict_mutex:
        if file_path not in file_locks:
            file_locks[file_path] = threading.Lock()
        return file_locks[file_path]

def cleanup_unused_locks() -> None:
    """清理不再使用的文件锁（可选的优化）"""
    with lock_dict_mutex:
        # 这里可以添加逻辑来清理长时间未使用的锁
        # 但需要小心，确保锁没有被使用
        pass

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 配置文件上传
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'md'}

def allowed_file(filename: Optional[str]) -> bool:
    return filename is not None and '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

model = SentenceTransformer("moka-ai/m3e-base")
SIMILARITY_THRESHOLD = 500.0


@app.route('/api/check_user', methods=['POST'])
def check_user():
    username = get_username()
    if username is not None:
        user_dir = os.path.join(UPLOAD_FOLDER, username)
        exists = os.path.exists(user_dir)
        return jsonify({"exists": exists})
    return jsonify({"exists": False}), 400


@app.route('/api/ask', methods=['POST'])
def ask():
    # 兼容 JSON 和 form
    if request.is_json:
        data = request.get_json()
        question = data.get('query')
        top_k = int(data.get('resultsPerPage', 5))
        username = data.get('username', 'default')
    else:
        question = request.form.get('question')
        top_k = int(request.form.get('top_k', 5))
        username = request.form.get('username', 'default')
    print(f"接收到的用户名: {username}")
    if not question:
        return jsonify({"error": "缺少 query/question 参数"}), 400

    if username is None:
        return jsonify({"error": "无效的用户名"}), 400
        
    user_dir = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(user_dir, exist_ok=True)
    notes_path = os.path.join(user_dir, "notes.json")

    # 只读取该用户的 notes.json
    if not os.path.exists(notes_path):
        return jsonify({"error": "知识库为空，请先上传文件"}), 400

    with open(notes_path, "r", encoding="utf-8") as f:
        user_notes = json.load(f)
    # print(f"加载的知识库: {user_notes}")
    if not user_notes:
        return jsonify({"error": "知识库为空，请先上传文件"}), 400

    texts = [note.get("content", "") for note in user_notes]
    embeddings = model.encode(texts)
    # 确保 embeddings 是正确的格式
    embeddings = np.array(embeddings).astype('float32')
    dim = embeddings.shape[1]
    user_index = faiss.IndexFlatL2(dim)
    user_index.add(embeddings)  # type: ignore

    query_vec = model.encode([question])
    query_vec = np.array(query_vec).astype('float32')
    D, I = user_index.search(query_vec, top_k)  # type: ignore

    results = []
    for score, idx in zip(D[0], I[0]):
        if score < SIMILARITY_THRESHOLD:
            note = user_notes[idx]
            file_id = note.get("fileId")
            
            # 查找对应的文件信息，获取downloadable状态
            file_downloadable = False
            file_title = note.get("title", "")
            if file_id:
                # 读取files.json查找文件信息
                files_path = os.path.join(user_dir, "files.json")
                if os.path.exists(files_path):
                    with open(files_path, "r", encoding="utf-8") as f:
                        files = json.load(f)
                    for file_entry in files:
                        if file_entry.get("id") == file_id:
                            file_downloadable = file_entry.get("meta", {}).get("downloadable", False)
                            file_title = file_entry.get("title", file_title)
                            break
            
            results.append({
                "id": note.get("id"),
                "fileId": file_id,
                "content": note.get("content", ""),
                "createdAt": note.get("createdAt"),
                "type": note.get("type", "abstract"),
                "title": note.get("title", ""),
                "author": note.get("author", ""),
                "date": note.get("date", ""),
                "page": note.get("page", ""),
                "score": float(score),
                "fileDownloadable": file_downloadable,  # 添加文件是否可下载的信息
                "fileTitle": file_title  # 添加文件标题信息
            })

    return jsonify({
        "results": results
    })

@app.route('/api/files', methods=['GET', 'POST', 'DELETE'])
def files():
    username = get_username()
    if username is None:
        return jsonify({'success': False, 'error': '无效的用户名'}), 400
        
    user_dir = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(user_dir, exist_ok=True)
    files_path = os.path.join(user_dir, "files.json")

    def load_files():
        if os.path.exists(files_path):
            with open(files_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_files(files):
        with open(files_path, "w", encoding="utf-8") as f:
            json.dump(files, f, ensure_ascii=False, indent=2)

    if request.method == 'GET':
        return jsonify(load_files())

    elif request.method == 'POST':
        data = request.get_json()
        if not data or "id" not in data:
            return jsonify({'success': False, 'error': '缺少文件id'}), 400
        files = load_files()
        if any(f["id"] == data["id"] for f in files):
            return jsonify({'success': False, 'error': '文件已存在'}), 200
        files.append(data)
        save_files(files)
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or "id" not in data:
            return jsonify({'success': False, 'error': '缺少文件id'}), 400
        files = load_files()
        files = [f for f in files if f["id"] != data["id"]]
        save_files(files)
        return jsonify({'success': True})
    
    # 如果方法不匹配，返回错误
    return jsonify({'success': False, 'error': '不支持的方法'}), 405

@app.route('/api/notes', methods=['GET', 'POST', 'DELETE'])
def notes_api():
    username = get_username()
    if username is None:
        return jsonify({'success': False, 'error': '无效的用户名'}), 400
        
    user_dir = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(user_dir, exist_ok=True)

    notes_path = os.path.join(user_dir, "notes.json")
    file_lock = get_file_lock(notes_path)

    def load_notes():
        if os.path.exists(notes_path):
            with open(notes_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_notes(notes):
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(notes_path, "w", encoding="utf-8") as f:
                    json.dump(notes, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(0.1 * (attempt + 1))  # 递增延迟
        return False

    if request.method == 'GET':
        file_id = request.args.get("fileId")
        with file_lock:  # 读取时也加锁，确保一致性
            notes = load_notes()
            if file_id:
                notes = [n for n in notes if n.get("fileId") == file_id]
        return jsonify(notes)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or "content" not in data:
            return jsonify({'success': False, 'error': '缺少内容'}), 400
        
        with file_lock:  # 整个读-修改-写操作加锁
            notes = load_notes()
            # 检查重复（基于内容和fileId）
            for existing_note in notes:
                if (existing_note.get("content") == data["content"] and 
                    existing_note.get("fileId") == data.get("fileId")):
                    return jsonify({'success': False, 'error': '该内容已存在，不重复添加'}), 200
            
            notes.append(data)
            save_notes(notes)
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '缺少参数'}), 400
            
        with file_lock:  # 整个读-修改-写操作加锁
            notes = load_notes()
            original_length = len(notes)
            
            if data.get("fileId"):
                notes = [n for n in notes if n.get("fileId") != data["fileId"]]
            elif data.get("id"):
                notes = [n for n in notes if n.get("id") != data["id"]]
            else:
                return jsonify({'success': False, 'error': '缺少删除参数'}), 400
            
            if len(notes) == original_length:
                return jsonify({'success': False, 'error': '未找到要删除的笔记'}), 404
                
            save_notes(notes)
        return jsonify({'success': True})
    
    # 如果方法不匹配，返回错误
    return jsonify({'success': False, 'error': '不支持的方法'}), 405

def get_username() -> str:
    """获取并验证用户名"""
    username = None
    
    if request.args.get("username"):
        username = request.args.get("username")
    elif request.is_json:
        data = request.get_json(silent=True)
        if data and data.get("username"):
            username = data.get("username")
    elif request.form.get("username"):
        username = request.form.get("username")
    
    if not username:
        username = "default"
    
    # 清理用户名，防止路径遍历攻击
    username = re.sub(r'[^\w\-_.]', '', username)
    if not username:
        username = "default"
    
    # 注册用户活动
    register_user_activity(username)
    
    return username

@app.route('/api/create_user', methods=['POST'])
def create_user():
    username = get_username()
    user_dir = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(user_dir, exist_ok=True)
    return jsonify({"success": True})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    try:
        username = get_username()
        if not username:
            return jsonify({'success': False, 'error': '用户名不能为空'}), 400
        
        # 检查是否有文件在请求中
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        file = request.files['file']
        
        # 如果用户没有选择文件，浏览器提交空的文件名
        if not file.filename or file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            # 创建用户文件夹
            user_dir = os.path.join(UPLOAD_FOLDER, username)
            os.makedirs(user_dir, exist_ok=True)
            
            # 生成安全的文件名（避免路径遍历攻击）
            if file.filename is not None:
                filename = secure_filename(file.filename)
            else:
                return jsonify({'success': False, 'error': '文件名无效'}), 400
            
            # 为文件生成唯一ID
            file_id = str(uuid.uuid4()) + filename.replace("/", "_").replace("\\", "_")
            
            # 保存文件到用户目录
            file_path = os.path.join(user_dir, filename)
            file.save(file_path)
            
            # 读取或创建 files.json
            files_path = os.path.join(user_dir, "files.json")
            
            def load_files():
                if os.path.exists(files_path):
                    with open(files_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                return []

            def save_files(files):
                with open(files_path, "w", encoding="utf-8") as f:
                    json.dump(files, f, ensure_ascii=False, indent=2)
            
            # 创建文件条目
            files = load_files()
            
            # 检查文件是否已存在
            if any(f["title"] == filename for f in files):
                return jsonify({'success': False, 'error': '文件已存在'}), 400
            
            # 创建文件信息条目
            file_entry = {
                "id": file_id,
                "title": filename,
                "meta": {
                    "title": filename,
                    "author": "",
                    "date": "",
                    "page": "",
                    "type": "uploaded",
                    "downloadable": True,  # 标记该文件可以下载
                    "file_size": os.path.getsize(file_path),
                    "upload_time": os.path.getctime(file_path),
                    "file_extension": filename.rsplit('.', 1)[1].lower() if '.' in filename else ""
                }
            }
            
            # 添加到文件列表
            files.append(file_entry)
            save_files(files)
            
            return jsonify({
                'success': True, 
                'message': '文件上传成功',
                'fileId': file_id,  # 返回文件ID供前端使用
                'file_info': file_entry
            })
        else:
            return jsonify({
                'success': False, 
                'error': f'不支持的文件类型。支持的类型: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'上传失败: {str(e)}'}), 500

@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """下载文件"""
    try:
        username = get_username()
        if not username:
            return jsonify({'success': False, 'error': '用户名不能为空'}), 400
        
        user_dir = os.path.join(UPLOAD_FOLDER, username)
        files_path = os.path.join(user_dir, "files.json")
        
        # 从 files.json 中查找文件信息
        if not os.path.exists(files_path):
            return jsonify({'success': False, 'error': '文件列表不存在'}), 404
        
        with open(files_path, "r", encoding="utf-8") as f:
            files = json.load(f)
        
        # 查找对应的文件
        target_file = None
        for file_entry in files:
            if file_entry.get("id") == file_id and file_entry.get("meta", {}).get("downloadable", False):
                target_file = file_entry
                break
        
        if not target_file:
            return jsonify({'success': False, 'error': '文件不存在或不可下载'}), 404
        
        # 构建文件路径
        filename = target_file.get("title")
        file_path = os.path.join(user_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': '物理文件不存在'}), 404
        
        # 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename  # 使用原始文件名
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/files/list', methods=['GET'])
def list_uploaded_files():
    """获取用户上传的文件列表"""
    try:
        username = get_username()
        if not username:
            return jsonify({'success': False, 'error': '用户名不能为空'}), 400
        
        user_files_dir = os.path.join(UPLOAD_FOLDER, username, 'files')
        
        if not os.path.exists(user_files_dir):
            return jsonify({'success': True, 'files': []})
        
        files_list = []
        for filename in os.listdir(user_files_dir):
            file_path = os.path.join(user_files_dir, filename)
            if os.path.isfile(file_path):
                file_id = filename.split('.')[0]  # 获取文件ID
                file_info = {
                    'id': file_id,
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'upload_time': os.path.getctime(file_path)
                }
                files_list.append(file_info)
        
        return jsonify({'success': True, 'files': files_list})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'获取文件列表失败: {str(e)}'}), 500

@app.route('/api/files/delete/<file_id>', methods=['DELETE'])
def delete_uploaded_file(file_id):
    """删除上传的文件"""
    try:
        username = get_username()
        if not username:
            return jsonify({'success': False, 'error': '用户名不能为空'}), 400
        
        user_dir = os.path.join(UPLOAD_FOLDER, username)
        files_path = os.path.join(user_dir, "files.json")
        
        print(f"尝试删除文件，用户: {username}, file_id: {file_id}")
        print(f"files.json 路径: {files_path}")
        print(f"files.json 是否存在: {os.path.exists(files_path)}")
        
        # 从 files.json 中查找并删除文件信息
        if not os.path.exists(files_path):
            return jsonify({'success': False, 'error': '文件列表不存在'}), 404
        
        with open(files_path, "r", encoding="utf-8") as f:
            files = json.load(f)
        
        print(f"当前文件列表: {files}")
        
        # 查找要删除的文件
        target_file = None
        for file_entry in files:
            if file_entry.get("id") == file_id:
                target_file = file_entry
                break
        
        if not target_file:
            print(f"未找到文件，file_id: {file_id}")
            return jsonify({'success': False, 'error': '文件不存在'}), 404
        
        print(f"找到目标文件: {target_file}")
        
        # 删除物理文件
        filename = target_file.get("title")
        file_path = os.path.join(user_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"已删除物理文件: {file_path}")
        
        # 从files.json中删除条目
        files = [f for f in files if f.get("id") != file_id]
        
        with open(files_path, "w", encoding="utf-8") as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
        
        print(f"文件删除成功")
        return jsonify({'success': True, 'message': '文件删除成功'})
            
    except Exception as e:
        print(f"删除文件时出现异常: {str(e)}")
        return jsonify({'success': False, 'error': f'删除失败: {str(e)}'}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """获取系统状态信息"""
    try:
        return jsonify({
            'success': True,
            'active_users': get_active_users_count(),
            'total_file_locks': len(file_locks),
            'upload_folder': UPLOAD_FOLDER,
            'server_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


