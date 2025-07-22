from flask import current_app as app
from pyfiles.database import db
from pyfiles.models import User,Role

def create_tables():
    with app.app_context():
        db.create_all()
        user_role = Role.query.filter_by(name='user').first()
        admin_role = Role.query.filter_by(name='admin').first()

        if not user_role:
            user_role = Role(name='user')
            db.session.add(user_role)

        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)

        db.session.commit()


        admin = User.query.filter_by(email='admin@gmail.com').first()
        if not admin:
            admin_role = Role.query.filter_by(name='admin').first()
            admin = User(
                email = 'admin@gmail.com',
                password = 'admin123',
                roles=[admin_role]
            )
            db.session.add(admin)

            # get_admin = User.query.filter_by(email="admin@gmail.com").first()
            # admin_role = Role.query.filter_by(name='admin').first()
            
            # user_role = UserRole(user_id=get_admin.id, role_id=admin_role.id)
            # db.session.add(user_role)

        db.session.commit()


        # User.query.all()
        # User.query.filter_by().all()
        # User.query.filter_by().first()