"""
Script to create an admin user
"""
import asyncio
from database.database import AsyncSessionLocal
from database.models import User, UserRole
from auth import get_password_hash


async def create_admin_user(email: str, password: str, full_name: str = "Admin User"):
    """Create an admin user"""
    async with AsyncSessionLocal() as session:
        admin_user = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            role=UserRole.ADMIN
        )
        session.add(admin_user)
        await session.commit()
        print(f"✓ Admin user created: {email}")


async def create_staff_user(email: str, password: str, full_name: str = "Staff User"):
    """Create a staff user"""
    async with AsyncSessionLocal() as session:
        staff_user = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            role=UserRole.STAFF
        )
        session.add(staff_user)
        await session.commit()
        print(f"✓ Staff user created: {email}")


async def main():
    """Create default admin and staff users"""
    print("Creating default users...")
    
    # Create admin user
    await create_admin_user(
        email="admin@infinitecompute.com",
        password="admin123",
        full_name="Admin User"
    )
    
    # Create staff user
    await create_staff_user(
        email="staff@infinitecompute.com",
        password="staff123",
        full_name="Staff User"
    )
    
    print("\nDefault users created successfully!")
    print("\nAdmin credentials:")
    print("  Email: admin@infinitecompute.com")
    print("  Password: admin123")
    print("\nStaff credentials:")
    print("  Email: staff@infinitecompute.com")
    print("  Password: staff123")
    print("\n⚠️  Remember to change these passwords in production!")


if __name__ == "__main__":
    asyncio.run(main())
