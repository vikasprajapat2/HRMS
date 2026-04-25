import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from database import db
from models import Employee, Document, Notification
import uuid

bp = Blueprint('document', __name__, url_prefix='/document')

def get_doc_upload_folder():
    folder = os.path.join(current_app.root_path, 'static', 'uploads', 'documents', 'official')
    os.makedirs(folder, exist_ok=True)
    return folder

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload/<int:employee_id>', methods=['POST'])
@login_required
def upload(employee_id):
    if current_user.role.name not in ['superadmin', 'hr']:
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    employee = Employee.query.get_or_404(employee_id)
    
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('employee.show', id=employee_id))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('employee.show', id=employee_id))
        
    title = request.form.get('title')
    doc_type = request.form.get('doc_type')
    
    if not title or not doc_type:
        flash('Title and Document Type are required.', 'danger')
        return redirect(url_for('employee.show', id=employee_id))
        
    if file and allowed_file(file.filename):
        # Generate secure unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{employee.unique_id}_{uuid.uuid4().hex[:8]}.{ext}"
        
        file_path = os.path.join(get_doc_upload_folder(), unique_filename)
        file.save(file_path)
        
        doc = Document(
            employee_id=employee.id,
            title=title,
            doc_type=doc_type,
            file_path=unique_filename,
            uploaded_by=current_user.id
        )
        db.session.add(doc)
        
        # Send Notification to employee
        if employee.email:
            from models import User
            user_account = User.query.filter_by(email=employee.email).first()
            if not user_account and '@' not in employee.email:
                user_account = User.query.filter_by(email=f"{employee.unique_id}@employee.local").first()
                
            if user_account:
                notif = Notification(
                    user_id=user_account.id,
                    message=f"A new official document '{title}' has been uploaded to your profile.",
                    type='system'
                )
                db.session.add(notif)
                
        db.session.commit()
        flash('Document uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG.', 'danger')
        
    return redirect(url_for('employee.show', id=employee_id))

@bp.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    # Check permissions
    if current_user.role.name not in ['superadmin', 'hr']:
        # If employee, ensure they can only download their own docs
        if current_user.role.name == 'employee':
            emp_email = current_user.email
            if '@employee.local' in emp_email:
                emp_unique_id = emp_email.split('@')[0]
                if doc.employee.unique_id != emp_unique_id:
                    abort(403)
            else:
                if doc.employee.email != emp_email:
                    abort(403)
        else:
            abort(403)
            
    folder = get_doc_upload_folder()
    return send_from_directory(folder, doc.file_path, as_attachment=False)

@bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    if current_user.role.name not in ['superadmin', 'hr']:
        abort(403)
        
    doc = Document.query.get_or_404(doc_id)
    employee_id = doc.employee_id
    
    # Try to remove physical file
    try:
        file_path = os.path.join(get_doc_upload_folder(), doc.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        pass
        
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted successfully!', 'success')
    
    return redirect(url_for('employee.show', id=employee_id))
