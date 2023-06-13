from werkzeug.security import generate_password_hash, check_password_hash

password = "digitalnao"
hashed_password = generate_password_hash(password)
print(hashed_password)

print(check_password_hash(hashed_password, password))
