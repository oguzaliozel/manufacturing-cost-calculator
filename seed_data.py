from database import Database

db = Database()

# Add some dummy materials for user_id = 1
db.add_material("Alüminyum 6061", "Plaka", 450.0, 15.0, 1)
db.add_material("Paslanmaz Çelik 304", "Plaka", 650.0, 12.0, 1)
db.add_material("Bakır Boru", "Metre", 120.0, 5.0, 1)

# Add some dummy processes for user_id = 1
db.add_process("CNC Kesim", "Saat", 250.0, 10.0, 1)
db.add_process("TIG Kaynak", "Saat", 180.0, 5.0, 1)
db.add_process("Elektrostatik Boya", "Adet", 35.0, 2.0, 1)

print("Initial data seeded successfully.")
