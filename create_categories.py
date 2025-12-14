import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "career_connect.settings")
django.setup()

from jobs.models import JobCategory

# Create job categories
categories = [
    {
        "name": "Information Technology",
        "description": "Software development, IT support, and technology roles",
    },
    {
        "name": "Healthcare",
        "description": "Medical, nursing, and healthcare professional positions",
    },
    {"name": "Finance", "description": "Banking, accounting, and financial services"},
    {
        "name": "Marketing",
        "description": "Digital marketing, content creation, and brand management",
    },
    {"name": "Sales", "description": "Business development and sales positions"},
    {"name": "Education", "description": "Teaching and educational roles"},
    {
        "name": "Engineering",
        "description": "Civil, mechanical, electrical engineering positions",
    },
    {"name": "Human Resources", "description": "HR management and recruitment"},
    {"name": "Customer Service", "description": "Customer support and service roles"},
    {"name": "Design", "description": "Graphic design, UI/UX, and creative positions"},
]

for cat in categories:
    JobCategory.objects.get_or_create(
        name=cat["name"], defaults={"description": cat["description"]}
    )

print("Successfully created job categories!")
