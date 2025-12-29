# seed.py atau tambahkan di akhir app.py
from app import app, db, User, Pet
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Daftar user baru (selain admin yang sudah ada)
        users_data = [
            ("budi", "budipass", "user"),
            ("siti", "sitipass", "user"),
            ("andi", "andipass", "user"),
            ("rini", "rinipass", "user"),
            ("dewa", "dewapass", "user"),
            ("luna", "lunapass", "user"),
            ("eko", "ekopass", "user"),
            ("maya", "mayapass", "user"),
            ("tono", "tonopass", "user"),
            ("vina", "vinapass", "user"),
        ]

        created_users = []
        for username, password, role in users_data:
            if not User.query.filter_by(username=username).first():
                user = User(
                    username=username,
                    password=generate_password_hash(password),
                    role=role
                )
                db.session.add(user)
                db.session.commit()
                created_users.append(user)
                print(f"User {username} dibuat")
            else:
                user = User.query.filter_by(username=username).first()
                created_users.append(user)

        # Daftar 20 hewan
        pets_data = [
            ("Milo", "Kucing Persia", 3, "budi"),
            ("Bella", "Anjing Golden Retriever", 5, "budi"),
            ("Oren", "Kucing Kampung", 2, "siti"),
            ("Kitty", "Kucing Anggora", 4, "siti"),
            ("Rocky", "Anjing Bulldog", 6, "andi"),
            ("Luna", "Kucing Scottish Fold", 1, "andi"),
            ("Coco", "Kelinci Holland Lop", 2, "rini"),
            ("Max", "Anjing Pomeranian", 3, "rini"),
            ("Snowball", "Kucing Himalaya", 4, "dewa"),
            ("Bruno", "Anjing German Shepherd", 7, "dewa"),
            ("Momo", "Kucing Maine Coon", 2, "luna"),
            ("Choco", "Anjing Beagle", 5, "luna"),
            ("Boni", "Kelinci Netherland Dwarf", 1, "eko"),
            ("Tiger", "Kucing Bengal", 3, "eko"),
            ("Daisy", "Anjing Shih Tzu", 4, "maya"),
            ("Simba", "Kucing Persia", 6, "maya"),
            ("Blacky", "Anjing Labrador", 2, "tono"),
            ("Whisky", "Kucing British Shorthair", 3, "tono"),
            ("Fluffy", "Kelinci Lionhead", 2, "vina"),
            ("Leo", "Kucing Ragdoll", 5, "vina"),
        ]

        for name, species, age, owner_username in pets_data:
            owner = User.query.filter_by(username=owner_username).first()
            if owner and not Pet.query.filter_by(name=name, owner_id=owner.id).first():
                pet = Pet(
                    name=name,
                    species=species,
                    age=age,
                    owner_id=owner.id
                )
                db.session.add(pet)
                print(f"Hewan {name} ({species}) ditambahkan untuk {owner_username}")
        db.session.commit()
        print("Semua 20 data hewan berhasil di-insert!")

# Jalankan sekali
if __name__ == '__main__':
    seed_data()