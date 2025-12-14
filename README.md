# CareerConnect - Job Board Platform

A comprehensive Django REST API for a job board application with two user roles: **Employers** and **Job Seekers**.

## Features

### 1. User Authentication

- Two user roles: Employer and Job Seeker
- User registration, login, and logout
- Email verification system
- Only verified users can log in
- JWT-based authentication

### 2. Job Listings

- Employers can create, update, and delete job listings
- Job details include: title, description, requirements, location, category, employment type, salary range
- Job listings display with employer information and application count

### 3. Job Details & Applications

- Detailed view of job listings
- Job Seekers can apply with resume and cover letter
- Automatic email notifications on application submission

### 4. User Dashboards

**Employer Dashboard:**

- Manage posted job listings
- View all applications received
- Update job details
- Track application statistics

**Job Seeker Dashboard:**

- Track job applications and their status
- Manage resumes and profiles
- View application history

### 5. Job Categories

- Jobs categorized by industry (IT, Healthcare, Finance, etc.)
- Filter job listings by category
- Category-wise job count

### 6. Email Notifications

- Registration confirmation with verification link
- Application confirmation to job seekers
- New application notification to employers

### 7. Resume Management

- Job Seekers can upload multiple resumes
- Set primary resume
- Secure file storage
- Update or delete resumes

### 8. Application Status Tracking

- Four status levels: Pending, Reviewed, Accepted, Rejected
- Employers can update application status
- Job Seekers can track application progress

### 9. Employer Reviews

- Job Seekers can review employers
- Rating system (1-5 stars)
- Written comments
- Public review display

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup Steps

1. **Create and activate virtual environment:**

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run migrations:**

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create superuser:**

```bash
python manage.py createsuperuser
```

5. **Run development server:**

```bash
python manage.py runserver
```

6. **Access the application:**

- API: http://localhost:8000/
- Admin Panel: http://localhost:8000/admin/
- Swagger Documentation: http://localhost:8000/swagger/

## API Endpoints

### Authentication (`/api/accounts/`)

- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/verify-email/` - Email verification
- `POST /api/accounts/login/` - User login (JWT)
- `POST /api/accounts/token/refresh/` - Refresh JWT token
- `GET /api/accounts/profile/` - Get user profile
- `PATCH /api/accounts/profile/` - Update user profile

### Jobs (`/api/jobs/`)

#### Categories

- `GET /api/jobs/categories/` - List all categories
- `GET /api/jobs/categories/{id}/` - Category details

#### Job Listings

- `GET /api/jobs/listings/` - List all active jobs (with filtering)
- `POST /api/jobs/listings/` - Create job (Employer only)
- `GET /api/jobs/listings/{id}/` - Job details
- `PATCH /api/jobs/listings/{id}/` - Update job (Employer only)
- `DELETE /api/jobs/listings/{id}/` - Delete job (Employer only)
- `GET /api/jobs/listings/my_listings/` - Employer's job listings
- `GET /api/jobs/listings/{id}/applications/` - Applications for a job (Employer only)

#### Applications

- `GET /api/jobs/applications/` - List applications
- `POST /api/jobs/applications/` - Apply for job (Job Seeker only)
- `GET /api/jobs/applications/{id}/` - Application details
- `PATCH /api/jobs/applications/{id}/update_status/` - Update status (Employer only)
- `GET /api/jobs/applications/my_applications/` - Job Seeker's applications

#### Resumes

- `GET /api/jobs/resumes/` - List user resumes (Job Seeker only)
- `POST /api/jobs/resumes/` - Upload resume (Job Seeker only)
- `GET /api/jobs/resumes/{id}/` - Resume details
- `PATCH /api/jobs/resumes/{id}/` - Update resume
- `DELETE /api/jobs/resumes/{id}/` - Delete resume
- `POST /api/jobs/resumes/{id}/set_primary/` - Set as primary resume

#### Reviews

- `GET /api/jobs/reviews/` - List all reviews
- `POST /api/jobs/reviews/` - Create review (Job Seeker only)
- `GET /api/jobs/reviews/{id}/` - Review details
- `PATCH /api/jobs/reviews/{id}/` - Update review
- `DELETE /api/jobs/reviews/{id}/` - Delete review

#### Dashboard

- `GET /api/jobs/dashboard/` - Get dashboard data (role-based)

## Filtering & Search

### Job Listings Support:

- **Filtering:** category, employment_type, location, salary range
- **Search:** title, description, requirements, location
- **Ordering:** created_at, title, salary_min

Example:

```
GET /api/jobs/listings/?category=1&employment_type=full_time&search=python&ordering=-created_at
```

## Data Models

### User Model

- Email (unique, used for login)
- User Type (employer/job_seeker)
- Email verification status
- Company name (for employers)
- Bio, phone number

### Job Listing

- Title, description, requirements
- Location, category, employment type
- Salary range
- Active status
- Application deadline

### Job Application

- Job reference
- Applicant reference
- Resume file
- Cover letter
- Status (pending/reviewed/accepted/rejected)

### Resume

- User reference
- Title, file
- Primary status

### Employer Review

- Employer reference
- Reviewer reference
- Rating (1-5)
- Comment

## Email Configuration

By default, emails are printed to console (development mode). To use real email:

Update `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Testing

Access the Swagger documentation at `/swagger/` to test all endpoints interactively.

### Quick Test Flow:

1. Register as employer: `POST /api/accounts/register/`
2. Verify email using token from console
3. Login: `POST /api/accounts/login/`
4. Create job listing: `POST /api/jobs/listings/`
5. Register as job seeker
6. Apply for job: `POST /api/jobs/applications/`
7. Check dashboard: `GET /api/jobs/dashboard/`

## Security Features

- JWT-based authentication
- Email verification required
- Role-based permissions
- Owner-only edit permissions
- File upload validation

## Technologies Used

- Django 5.1.5
- Django REST Framework
- Simple JWT for authentication
- drf-yasg for API documentation
- django-filter for filtering
- SQLite database (development)

## Project Structure

```
CareerConnect/
├── accounts/          # User authentication & management
├── api/               # Centralized API routing
├── jobs/              # Job listings, applications, resumes, reviews
├── career_connect/    # Main project settings
├── media/             # Uploaded files (resumes)
└── manage.py
```

## Future Enhancements

- Advanced search with Elasticsearch
- Real-time notifications with WebSockets
- Video interview scheduling
- Skills matching algorithm
- Company profiles
- Saved jobs/bookmarks
- Application analytics

## License

This project is licensed under the MIT License.

## Contact

For questions or support, contact: contact@careerconnect.com
