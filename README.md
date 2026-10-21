# Alzheimer's Support — Intelligent Face Recognition & Care System for Alzheimer's Patients

A complete web-based healthcare platform that combines **AI-powered face recognition** (DeepFace + VGG-Face) with **structured medical management** to support Alzheimer's patients, their doctors, and caregivers.

---

## 🎯 Features

- **Face Recognition** — Embedding-based identification using VGG-Face (512-d vectors) with cosine similarity matching
- **Voice Announcements** — Browser TTS announces "This is your daughter, Priya" on recognition
- **Three Role-Based Modules** — Admin / Doctor / Patient
- **Medicine Reminders** — Doctor-prescribed + self-added with adherence tracking
- **Appointment Management** — Scheduling, rescheduling, completion tracking
- **Custom Alerts** — Hydration, exercise, routine reminders
- **Emergency Contacts** — Next-of-kin with one-tap call
- **Approval Workflow** — Patient requests, doctor approval/rejection
- **In-App Notifications** — Real-time across all roles
- **Activity Logs** — Full system audit trail

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Django 4.2 |
| Database | MySQL 8.0+ (via mysqlclient) |
| Frontend | HTML5, CSS3, Bootstrap 5.3, JavaScript, jQuery, AJAX |
| AI / ML | DeepFace, VGG-Face, TensorFlow, OpenCV, NumPy |
| Theme | Medical Healthcare (white + teal/blue) |

---

## 📁 Project Structure

```
alzheimer_care_system/
├── manage.py
├── requirements.txt
├── README.md
├── alzheimer_care_system/      # Main Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                       # Public pages, auth, shared models
├── admin_app/                  # Admin dashboard + doctor management
├── doctor_app/                 # Doctor dashboard, prescriptions, appointments
├── user_app/                   # Patient dashboard, medicines, alerts, contacts
├── face_recognition_app/       # DeepFace VGG-Face enrollment + recognition
├── templates/                  # All HTML templates
│   ├── base_public.html
│   ├── base_dashboard.html
│   ├── public/  auth/  admin_app/  doctor_app/  user_app/  face_recognition_app/
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
└── media/                      # Uploaded photos + known_faces.pkl
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites

- **Python 3.10+** (3.10 or 3.11 recommended; TensorFlow 2.13 doesn't fully support 3.12)
- **MySQL 8.0+** running locally
- **Git** (optional)
- **Visual C++ Build Tools** (Windows only — required for mysqlclient + dlib if used)
- A working **webcam** for real-time recognition

### 2. Clone / Extract the Project

```bash
cd path/to/your/projects
# Extract the ZIP, then:
cd alzheimer_care_system
```

### 3. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note on DeepFace:** On first run, DeepFace downloads the VGG-Face model weights (~580 MB) automatically. Ensure you have internet access on first launch.

**Troubleshooting mysqlclient install:**

- **Windows:** Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/), then `pip install mysqlclient`.
- **Ubuntu/Debian:** `sudo apt install python3-dev default-libmysqlclient-dev build-essential`
- **macOS:** `brew install mysql-client pkg-config`

### 5. Create the MySQL Database

Open MySQL CLI or Workbench:

```sql
CREATE DATABASE alzheimer_care_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Configure Database Credentials

Open `alzheimer_care_system/settings.py` and update:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alzheimer_care_db',
        'USER': 'root',                   # your MySQL user
        'PASSWORD': '', # your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 7. Run Migrations

```bash
python manage.py makemigrations core admin_app doctor_app user_app face_recognition_app
python manage.py migrate
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 🚀 First-Time Setup Flow

1. **Open the homepage** → `http://127.0.0.1:8000/`
2. **Create Admin Account** → Go to `/setup/` (one-time only)
3. **Login as Admin** → Add doctors from the Doctors page
4. **Register as Patient** → From the public Register page
5. **Patient logs in** → Goes to *Medical Details* and assigns a doctor
6. **Doctor logs in** → Sees patient under *My Patients*, can prescribe medicines and schedule appointments
7. **Patient enrolls faces** → Goes to *Known Faces* → *Enroll New Face*
8. **Patient runs recognition** → Goes to *Recognize Visitor*, allows camera, captures → voice announces the visitor

---

## 🧠 How Face Recognition Works

```
ENROLLMENT
   1. Patient uploads 1 primary + 2-4 extra photos
   2. DeepFace.represent() extracts 512-d embedding per image (VGG-Face)
   3. Embeddings averaged + L2-normalized
   4. Stored in media/known_faces.pkl under patient_<id> key

RECOGNITION
   1. Webcam captures frame → base64 → POSTed to /face/recognize/api/
   2. Server decodes, saves temp file, extracts query embedding
   3. Computes cosine distance against all enrolled embeddings
   4. If distance < 0.68 → MATCH (returns name + relationship + confidence%)
   5. Browser receives JSON → renders result + speaks via SpeechSynthesisUtterance
```

---

## 🔐 Default URLs

| URL | Purpose |
|---|---|
| `/` | Public landing page |
| `/features/` `/about/` `/contact/` | Public pages |
| `/setup/` | One-time admin setup |
| `/login/` | Login (Admin / Doctor / Patient) |
| `/register/` | Patient self-registration |
| `/admin-panel/dashboard/` | Admin dashboard |
| `/doctor/dashboard/` | Doctor dashboard |
| `/user/dashboard/` | Patient dashboard |
| `/face/recognize/` | Real-time face recognition |
| `/face/known/` | Known faces list |
| `/django-admin/` | Django built-in admin (use superuser) |

---

## 📦 Models Overview

| App | Models |
|---|---|
| `core` | Admin, Doctor, Patient, Notification, ActivityLog |
| `doctor_app` | Appointment, Prescription, ConsultationNote, ApprovalRequest |
| `user_app` | MedicalDetail, Medicine, MedicineLog, Alert, EmergencyContact |
| `face_recognition_app` | KnownFace, FaceImage, RecognitionLog |

---

## ⚠️ Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` in `settings.py`
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` correctly
- [ ] Use environment variables for DB credentials (e.g., `python-decouple`)
- [ ] Set up HTTPS (camera access requires HTTPS on non-localhost)
- [ ] Use Gunicorn + Nginx instead of `runserver`
- [ ] Configure proper static/media serving (e.g., WhiteNoise or S3)
- [ ] Set up regular backups for `media/known_faces.pkl` and MySQL DB
- [ ] Add rate limiting on `/face/recognize/api/`
- [ ] Review password policies in `AUTH_PASSWORD_VALIDATORS`

---

## 🐛 Troubleshooting

**"No face detected" during enrollment**
→ Use clear, front-facing, well-lit photos. The face should occupy ≥25% of the image.

**Camera doesn't start**
→ Browsers require HTTPS for camera access on non-localhost. On localhost, allow camera permission in the browser prompt.

**TensorFlow/DeepFace memory errors**
→ Close other heavy apps. VGG-Face needs ~2 GB RAM. Consider GPU acceleration for production.

**"Table doesn't exist" after migrations**
→ Run `python manage.py makemigrations` for each app explicitly:
```bash
python manage.py makemigrations core
python manage.py makemigrations doctor_app
python manage.py makemigrations user_app
python manage.py makemigrations face_recognition_app
python manage.py migrate
```

**MySQL connection refused**
→ Ensure MySQL service is running: `sudo systemctl start mysql` (Linux) or open MySQL Workbench (Windows).

---

## 📚 Academic Context

This system was designed based on the project documents:
- **Abstract** — Intelligent Face Recognition for Enhancing Care and Reminder System for Alzheimer's Patients
- **Modules** — Admin, Doctor, User specifications
- **DFD** — Level 0 + Level 1 (Admin, Doctor, User)

The recognition approach follows the embedding-based methodology described in the abstract: pre-trained VGG-Face for feature extraction, 512-d embeddings, cosine similarity for matching, no retraining required when adding new people.

---

## 📄 License

This is a student/academic project. Adapt freely for educational purposes.

---

## 👋 Credits

Built with ❤️ for cognitive wellness. Theme: Medical Healthcare (clean white + teal/blue).
