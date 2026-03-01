"""
Seed script — run once after the containers are up.
Populates:
  - Role categories
  - Target roles with keywords
  - Skills fixed list
  - Todo items per category per level
  - Default admin user
  - 2 sample students
  - 2 sample alumni

Usage:
  docker compose exec api python seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
from app.database import SessionLocal, engine, Base
from app.models.models import (
    RoleCategory, TargetRole, Skill, TodoItem, Profile,
    AlumniPublicProfile, LevelEnum, RoleEnum
)
import app.models.models  # noqa - ensures all tables are registered

Base.metadata.create_all(bind=engine)
db = SessionLocal()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed():
    # -----------------------------------------------------------------------
    # Categories
    # -----------------------------------------------------------------------
    categories_data = [
        "Software Engineering",
        "Cloud & DevOps",
        "Cybersecurity",
        "Data Science & ML",
        "Product & Business",
    ]
    categories = {}
    for name in categories_data:
        existing = db.query(RoleCategory).filter(RoleCategory.name == name).first()
        if not existing:
            cat = RoleCategory(name=name)
            db.add(cat)
            db.flush()
            categories[name] = cat
        else:
            categories[name] = existing
    db.commit()
    print("✓ Categories seeded")

    # -----------------------------------------------------------------------
    # Target Roles
    # -----------------------------------------------------------------------
    roles_data = [
        # (name, category_name, keywords)
        ("Software Engineer", "Software Engineering", ["software", "developer", "engineer", "backend", "frontend", "fullstack"]),
        ("Frontend Developer", "Software Engineering", ["frontend", "react", "vue", "angular", "ui", "web"]),
        ("Backend Developer", "Software Engineering", ["backend", "api", "server", "django", "fastapi", "node"]),
        ("Cloud Engineer", "Cloud & DevOps", ["cloud", "aws", "azure", "gcp", "infrastructure", "devops", "sre"]),
        ("DevOps Engineer", "Cloud & DevOps", ["devops", "cicd", "docker", "kubernetes", "terraform", "ansible"]),
        ("Cloud Security Engineer", "Cybersecurity", ["cloud", "security", "aws", "iam", "infosec", "sre", "devops"]),
        ("Security Analyst", "Cybersecurity", ["security", "analyst", "soc", "threat", "vulnerability"]),
        ("Penetration Tester", "Cybersecurity", ["pentest", "security", "ethical", "hacking", "red team"]),
        ("Data Scientist", "Data Science & ML", ["data", "scientist", "ml", "machine learning", "analytics"]),
        ("ML Engineer", "Data Science & ML", ["ml", "machine learning", "ai", "deep learning", "model"]),
        ("Product Manager", "Product & Business", ["product", "manager", "pm", "strategy", "roadmap"]),
        ("Business Analyst", "Product & Business", ["business", "analyst", "requirements", "process"]),
    ]
    for name, cat_name, keywords in roles_data:
        existing = db.query(TargetRole).filter(TargetRole.name == name).first()
        if not existing:
            db.add(TargetRole(name=name, category_id=categories[cat_name].id, keywords=keywords))
    db.commit()
    print("✓ Target roles seeded")

    # -----------------------------------------------------------------------
    # Skills (fixed list)
    # -----------------------------------------------------------------------
    skills_data = [
        # Software Engineering
        ("Python", "Software Engineering"),
        ("JavaScript", "Software Engineering"),
        ("TypeScript", "Software Engineering"),
        ("Java", "Software Engineering"),
        ("C++", "Software Engineering"),
        ("Go", "Software Engineering"),
        ("React", "Software Engineering"),
        ("Node.js", "Software Engineering"),
        ("FastAPI", "Software Engineering"),
        ("Django", "Software Engineering"),
        ("PostgreSQL", "Software Engineering"),
        ("MongoDB", "Software Engineering"),
        ("REST APIs", "Software Engineering"),
        ("Git", "Software Engineering"),
        # Cloud & DevOps
        ("AWS", "Cloud & DevOps"),
        ("Azure", "Cloud & DevOps"),
        ("GCP", "Cloud & DevOps"),
        ("Docker", "Cloud & DevOps"),
        ("Kubernetes", "Cloud & DevOps"),
        ("Terraform", "Cloud & DevOps"),
        ("Ansible", "Cloud & DevOps"),
        ("Linux", "Cloud & DevOps"),
        ("CI/CD", "Cloud & DevOps"),
        ("GitHub Actions", "Cloud & DevOps"),
        ("Networking", "Cloud & DevOps"),
        ("Bash Scripting", "Cloud & DevOps"),
        # Cybersecurity
        ("IAM", "Cybersecurity"),
        ("Network Security", "Cybersecurity"),
        ("SIEM", "Cybersecurity"),
        ("Penetration Testing", "Cybersecurity"),
        ("Vulnerability Assessment", "Cybersecurity"),
        ("Firewalls & UFW", "Cybersecurity"),
        ("OWASP", "Cybersecurity"),
        # Data Science & ML
        ("Machine Learning", "Data Science & ML"),
        ("Deep Learning", "Data Science & ML"),
        ("TensorFlow", "Data Science & ML"),
        ("PyTorch", "Data Science & ML"),
        ("Pandas", "Data Science & ML"),
        ("SQL", "Data Science & ML"),
        ("Data Visualization", "Data Science & ML"),
        ("Statistics", "Data Science & ML"),
        # Product & Business
        ("Product Management", "Product & Business"),
        ("Agile / Scrum", "Product & Business"),
        ("Figma", "Product & Business"),
        ("Market Research", "Product & Business"),
        ("Excel / Sheets", "Product & Business"),
    ]
    for skill_name, cat_name in skills_data:
        existing = db.query(Skill).filter(Skill.name == skill_name).first()
        if not existing:
            db.add(Skill(name=skill_name, category_id=categories[cat_name].id))
    db.commit()
    print("✓ Skills seeded")

    # -----------------------------------------------------------------------
    # Todo Items
    # -----------------------------------------------------------------------
    todos_data = [
        # --- Cloud & DevOps ---
        ("Cloud & DevOps", LevelEnum.foundation, "Learn Linux fundamentals", "File system, permissions, systemd, SSH basics.", "https://linuxjourney.com"),
        ("Cloud & DevOps", LevelEnum.foundation, "Understand core networking", "IP addressing, DNS, TCP/UDP, subnetting.", "https://www.cloudflare.com/learning/network-layer/what-is-the-network-layer/"),
        ("Cloud & DevOps", LevelEnum.foundation, "Get comfortable with Git", "Create a GitHub account, commit, push, and open a PR.", "https://learngitbranching.js.org"),
        ("Cloud & DevOps", LevelEnum.foundation, "Study cloud basics", "Complete AWS Cloud Practitioner Essentials or Google Cloud Digital Leader free materials.", "https://explore.skillbuilder.aws/learn"),
        ("Cloud & DevOps", LevelEnum.skill_building, "Learn Docker", "Build images, run containers, write a docker-compose file.", "https://docs.docker.com/get-started/"),
        ("Cloud & DevOps", LevelEnum.skill_building, "Practice AWS core services", "Hands-on with EC2, S3, IAM, VPC, and Security Groups.", "https://aws.amazon.com/free/"),
        ("Cloud & DevOps", LevelEnum.skill_building, "Write Bash scripts", "Automate a server provisioning task with a shell script.", None),
        ("Cloud & DevOps", LevelEnum.skill_building, "Set up a home lab", "Run VMs, configure VLANs, and simulate a cloud-style network.", None),
        ("Cloud & DevOps", LevelEnum.internship_ready, "Learn Terraform basics", "Write IaC to provision an EC2 instance with a VPC.", "https://developer.hashicorp.com/terraform/tutorials"),
        ("Cloud & DevOps", LevelEnum.internship_ready, "Set up a CI/CD pipeline", "Use GitHub Actions to build, test, and deploy a Docker app.", None),
        ("Cloud & DevOps", LevelEnum.internship_ready, "Earn a cloud certification", "AWS Solutions Architect Associate or equivalent.", "https://aws.amazon.com/certification/"),
        ("Cloud & DevOps", LevelEnum.interview_ready, "Deploy a full project on AWS", "EC2 + RDS + ALB + S3 + IAM roles — document it on GitHub.", None),
        ("Cloud & DevOps", LevelEnum.interview_ready, "Practice system design", "Be able to explain scalability, availability, and fault tolerance.", "https://github.com/donnemartin/system-design-primer"),
        ("Cloud & DevOps", LevelEnum.interview_ready, "Prepare cloud interview questions", "Focus on networking, IAM, cost optimization, and security best practices.", None),

        # --- Cybersecurity ---
        ("Cybersecurity", LevelEnum.foundation, "Learn networking fundamentals", "OSI model, TCP/IP, firewalls, DNS, HTTP/HTTPS.", "https://www.professormesser.com/network-plus/"),
        ("Cybersecurity", LevelEnum.foundation, "Get comfortable with Linux", "Command line, file permissions, user management, log files.", "https://linuxjourney.com"),
        ("Cybersecurity", LevelEnum.foundation, "Study basic security concepts", "CIA triad, authentication vs authorization, encryption basics.", "https://www.coursera.org/learn/google-cybersecurity"),
        ("Cybersecurity", LevelEnum.skill_building, "Practice on TryHackMe or HackTheBox", "Complete beginner-friendly rooms covering OWASP Top 10.", "https://tryhackme.com"),
        ("Cybersecurity", LevelEnum.skill_building, "Learn IAM concepts deeply", "Users, roles, policies, least privilege, MFA.", None),
        ("Cybersecurity", LevelEnum.skill_building, "Set up a SIEM lab", "Install Splunk or ELK stack locally and ingest sample logs.", None),
        ("Cybersecurity", LevelEnum.internship_ready, "Earn CompTIA Security+", "Core industry cert that proves security fundamentals.", "https://www.comptia.org/certifications/security"),
        ("Cybersecurity", LevelEnum.internship_ready, "Learn cloud security", "AWS Security Specialty study guide, IAM policies, GuardDuty, CloudTrail.", None),
        ("Cybersecurity", LevelEnum.interview_ready, "Build a security homelab", "Simulate attacks, configure IDS, document your findings.", None),
        ("Cybersecurity", LevelEnum.interview_ready, "Prepare incident response scenarios", "Practice walking through a security incident end-to-end.", None),

        # --- Software Engineering ---
        ("Software Engineering", LevelEnum.foundation, "Pick a language and go deep", "Master Python or JavaScript fundamentals — loops, data structures, OOP.", "https://cs50.harvard.edu"),
        ("Software Engineering", LevelEnum.foundation, "Learn Git and GitHub", "Branching, merging, pull requests, .gitignore.", "https://learngitbranching.js.org"),
        ("Software Engineering", LevelEnum.skill_building, "Build a REST API", "Use FastAPI or Express.js to build a CRUD API with a database.", None),
        ("Software Engineering", LevelEnum.skill_building, "Learn SQL basics", "Joins, aggregations, indexes — use PostgreSQL.", "https://sqlzoo.net"),
        ("Software Engineering", LevelEnum.internship_ready, "Contribute to open source", "Find a beginner-friendly GitHub issue and open a PR.", "https://goodfirstissue.dev"),
        ("Software Engineering", LevelEnum.internship_ready, "Learn Docker basics", "Containerize your projects.", "https://docs.docker.com/get-started/"),
        ("Software Engineering", LevelEnum.interview_ready, "Practice DSA", "Solve 50+ LeetCode problems covering arrays, trees, graphs, DP.", "https://leetcode.com"),
        ("Software Engineering", LevelEnum.interview_ready, "Study system design", "Design a URL shortener, a message queue, and a social feed.", "https://github.com/donnemartin/system-design-primer"),

        # --- Data Science & ML ---
        ("Data Science & ML", LevelEnum.foundation, "Learn Python for data", "numpy, pandas, matplotlib basics.", "https://kaggle.com/learn"),
        ("Data Science & ML", LevelEnum.foundation, "Understand statistics", "Mean, median, distributions, hypothesis testing.", None),
        ("Data Science & ML", LevelEnum.skill_building, "Build ML models", "Linear regression, decision trees, random forests with scikit-learn.", "https://scikit-learn.org"),
        ("Data Science & ML", LevelEnum.skill_building, "Compete on Kaggle", "Join a beginner competition and submit your first notebook.", "https://kaggle.com"),
        ("Data Science & ML", LevelEnum.internship_ready, "Learn deep learning basics", "Neural networks with PyTorch or TensorFlow.", "https://fast.ai"),
        ("Data Science & ML", LevelEnum.internship_ready, "Build an end-to-end ML project", "Data collection → preprocessing → model → deployment.", None),
        ("Data Science & ML", LevelEnum.interview_ready, "Study ML system design", "Be able to design a recommendation system or fraud detection model.", None),
        ("Data Science & ML", LevelEnum.interview_ready, "Practice ML interview questions", "Bias-variance tradeoff, regularization, model evaluation metrics.", None),

        # --- Product & Business ---
        ("Product & Business", LevelEnum.foundation, "Learn product management basics", "Read 'Inspired' by Marty Cagan or take a free PM course.", None),
        ("Product & Business", LevelEnum.foundation, "Get comfortable with data", "Excel, Google Sheets, and basic SQL for product metrics.", None),
        ("Product & Business", LevelEnum.skill_building, "Learn Agile and Scrum", "Sprints, backlogs, user stories, retrospectives.", "https://www.scrum.org/resources"),
        ("Product & Business", LevelEnum.skill_building, "Create a product case study", "Pick a product you use and redesign one feature with justification.", None),
        ("Product & Business", LevelEnum.internship_ready, "Learn Figma", "Build low and high fidelity wireframes for your case study.", "https://www.figma.com/resource-library/"),
        ("Product & Business", LevelEnum.internship_ready, "Run user interviews", "Talk to 5 potential users and write up the findings.", None),
        ("Product & Business", LevelEnum.interview_ready, "Practice PM interview questions", "Estimation, design, strategy, and metrics questions.", "https://www.productalliance.com"),
        ("Product & Business", LevelEnum.interview_ready, "Build your PM portfolio", "Document 2-3 case studies with problem, solution, impact.", None),
    ]
    for cat_name, level, title, description, resource_url in todos_data:
        existing = db.query(TodoItem).filter(
            TodoItem.category_id == categories[cat_name].id,
            TodoItem.title == title
        ).first()
        if not existing:
            db.add(TodoItem(
                category_id=categories[cat_name].id,
                level=level,
                title=title,
                description=description,
                resource_url=resource_url,
            ))
    db.commit()
    print("✓ Todo items seeded")

    # -----------------------------------------------------------------------
    # Default Admin User
    # -----------------------------------------------------------------------
    if not db.query(Profile).filter(Profile.email == "admin@alumni.com").first():
        db.add(Profile(
            name="Admin",
            email="admin@alumni.com",
            password_hash=pwd.hash("admin123"),
            role=RoleEnum.admin,
        ))
        db.commit()
        print("✓ Admin user created — admin@alumni.com / admin123")
    else:
        print("  Admin user already exists")

    # -----------------------------------------------------------------------
    # Sample Students
    # -----------------------------------------------------------------------
    sample_students = [
        ("Arjun Mehta", "arjun@college.edu", "student123", "Information Technology", 2026),
        ("Priya Nair", "priya@college.edu", "student123", "Computer Science", 2026),
    ]
    for name, email, password, dept, batch in sample_students:
        if not db.query(Profile).filter(Profile.email == email).first():
            db.add(Profile(
                name=name,
                email=email,
                password_hash=pwd.hash(password),
                role=RoleEnum.student,
                department=dept,
                batch_year=batch,
            ))
    db.commit()
    print("✓ Sample students seeded")

    # -----------------------------------------------------------------------
    # Sample Alumni
    # -----------------------------------------------------------------------
    sample_alumni = [
        ("Karthik Rajan", "karthik@alumni.edu", "alumni123", "Information Technology", 2022, "Razorpay", "Cloud Security Engineer", "Bengaluru"),
        ("Sneha Iyer", "sneha@alumni.edu", "alumni123", "Computer Science", 2021, "Freshworks", "DevOps Engineer", "Chennai"),
    ]
    for name, email, password, dept, batch, company, job_title, location in sample_alumni:
        existing = db.query(Profile).filter(Profile.email == email).first()
        if not existing:
            alumnus = Profile(
                name=name,
                email=email,
                password_hash=pwd.hash(password),
                role=RoleEnum.alumni,
                department=dept,
                batch_year=batch,
            )
            db.add(alumnus)
            db.flush()
            db.add(AlumniPublicProfile(
                alumni_id=alumnus.id,
                company=company,
                job_title=job_title,
                location=location,
            ))
    db.commit()
    print("✓ Sample alumni seeded")

    print("\n✅ Seed complete.")
    print("\n--- Login credentials ---")
    print("Admin:   admin@alumni.com    / admin123")
    print("Student: arjun@college.edu   / student123")
    print("Student: priya@college.edu   / student123")
    print("Alumni:  karthik@alumni.edu  / alumni123")
    print("Alumni:  sneha@alumni.edu    / alumni123")


if __name__ == "__main__":
    seed()
    db.close()
