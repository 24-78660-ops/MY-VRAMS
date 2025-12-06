from db_con import DBConnection
from qr_generator import generate_user_qr

def generate_all():
    db = DBConnection()
    users = db.fetch("SELECT id, name, age, address, contact_number, department, sr_code, work_type FROM register")
    if not users:
        print("No users found.")
        return
    for u in users:
        user_id = u['id']
        sticker, qr_file = generate_user_qr(user_id, u['name'], u['age'], u['address'], u['contact_number'], u['department'], u['sr_code'], u['work_type'])
        db.update("UPDATE register SET sticker_code=?, qr_file=? WHERE id=?", (sticker, qr_file, user_id))
        print(f"[OK] {u['name']} -> {sticker} saved {qr_file}")
    db.close()

if __name__ == "__main__":
    generate_all()
