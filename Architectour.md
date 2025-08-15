📁 consultation_platform/
├── 📁 app/
│   ├── 📄 __init__.py
│   ├── 📄 main.py
│   ├── 📄 config.py
│   ├── 📄 database.py
│   ├── 📄 dependencies.py
│   │
│   ├── 📁 models/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base.py
│   │   ├── 📄 user.py
│   │   ├── 📄 consultant.py
│   │   ├── 📄 consultation.py
│   │   ├── 📄 payment.py
│   │   ├── 📄 message.py
│   │   ├── 📄 notification.py
│   │   └── 📄 system.py
│   │
│   ├── 📁 schemas/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user.py
│   │   ├── 📄 consultant.py
│   │   ├── 📄 consultation.py
│   │   ├── 📄 payment.py
│   │   ├── 📄 message.py
│   │   └── 📄 common.py
│   │
│   ├── 📁 api/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 deps.py
│   │   └── 📁 v1/
│   │       ├── 📄 __init__.py
│   │       ├── 📄 auth.py
│   │       ├── 📄 users.py
│   │       ├── 📄 consultants.py
│   │       ├── 📄 consultations.py
│   │       ├── 📄 payments.py
│   │       ├── 📄 messages.py
│   │       ├── 📄 live_chat.py
│   │       ├── 📄 notifications.py
│   │       ├── 📄 reviews.py
│   │       ├── 📄 support.py
│   │       └── 📄 admin.py
│   │
│   ├── 📁 services/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py
│   │   ├── 📄 user.py
│   │   ├── 📄 consultant.py
│   │   ├── 📄 consultation.py
│   │   ├── 📄 payment.py
│   │   ├── 📄 wallet.py
│   │   ├── 📄 message.py
│   │   ├── 📄 notification.py
│   │   ├── 📄 email.py
│   │   ├── 📄 sms.py
│   │   ├── 📄 file_storage.py
│   │   ├── 📄 video_call.py
│   │   └── 📄 backup.py
│   │
│   ├── 📁 core/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 security.py
│   │   ├── 📄 config.py
│   │   ├── 📄 exceptions.py
│   │   ├── 📄 middleware.py
│   │   └── 📄 logging.py
│   │
│   ├── 📁 utils/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 helpers.py
│   │   ├── 📄 validators.py
│   │   ├── 📄 date_utils.py
│   │   ├── 📄 file_utils.py
│   │   └── 📄 encryption.py
│   │
│   └── 📁 tasks/
│       ├── 📄 __init__.py
│       ├── 📄 celery_app.py
│       ├── 📄 email_tasks.py
│       ├── 📄 notification_tasks.py
│       ├── 📄 backup_tasks.py
│       └── 📄 cleanup_tasks.py
│
├── 📁 tests/
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py
│   ├── 📁 api/
│   ├── 📁 services/
│   └── 📁 utils/
│
├── 📁 alembic/
│   ├── 📄 env.py
│   ├── 📄 script.py.mako
│   └── 📁 versions/
│
├── 📁 scripts/
│   ├── 📄 init_db.py
│   ├── 📄 seed_data.py
│   └── 📄 backup.py
│
├── 📄 docker-compose.yml
├── 📄 Dockerfile
├── 📄 requirements.txt
├── 📄 .env.example
├── 📄 alembic.ini
└── 📄 README.md