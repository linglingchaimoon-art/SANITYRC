from app.database import SessionLocal, Base, engine
from app.models import License

Base.metadata.create_all(bind=engine)

db = SessionLocal()

license_key = "SANITY2X-OWNER-KEY"

existing = db.query(License).filter(License.license_key == license_key).first()

if not existing:
    license = License(
        license_key=license_key,
        owner="TJ",
        role="Owner",
        active=True
    )

    db.add(license)
    db.commit()
    print("License created.")
else:
    print("License already exists.")

db.close()