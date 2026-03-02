# seed_clients.py
from app import create_app, db
from app.models.client import Client
from app.models.user import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        clients_test = [
            ("Jean", "Dupont", "jean.dupont@email.com", "771234567", "Dakar, Sénégal"),
            ("Aminata", "Diallo", "aminata.diallo@email.com", "772345678", "Dakar, Sénégal"),
            ("Oumar", "Ndiaye", None, "773456789", None),
            ("Fatou", "Diop", "fatou.diop@email.com", "774567890", "Thiès, Sénégal"),
            ("Moussa", "Fall", "moussa.fall@email.com", "775678901", "Saint-Louis, Sénégal"),
            ("Marième", "Sow", "marieme.sow@email.com", "776789012", "Dakar, Sénégal"),
            ("Ibrahima", "Ba", None, "777890123", None),
            ("Aissatou", "Gueye", "aissatou.gueye@email.com", "778901234", "Dakar, Sénégal"),
        ]
        
        for prenom, nom, email, tel, adresse in clients_test:
            existing = Client.query.filter_by(phone=tel).first()
            if not existing:
                client = Client(
                    first_name=prenom,
                    last_name=nom,
                    email=email,
                    phone=tel,
                    address=adresse,
                    created_by=admin.id
                )
                db.session.add(client)
                print(f"✅ Client ajouté : {prenom} {nom}")
        
        db.session.commit()
        print("🎉 Clients de test ajoutés !")