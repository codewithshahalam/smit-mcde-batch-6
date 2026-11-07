# Task 14 - Command-Line Contact Manager.

import json
import os
import re
import shutil
import tempfile

class StorageError(Exception):
    pass


def load_contacts(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            content = handle.read()
        if not content.strip():
            return []
        data = json.loads(content)
        if not isinstance(data, list) or not all(isinstance(c, dict) for c in data):
            raise ValueError("top-level JSON must be a list of objects")
        return data
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as exc:
        backup = path + ".corrupt"
        try:
            shutil.copy2(path, backup)
        except OSError:
            backup = "(backup failed)"
        raise StorageError(f"{path} is corrupt ({exc}). Original kept; copy at {backup}.") from exc


def save_contacts(path, contacts):
    folder = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(contacts, handle, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


PHONE_RE = re.compile(r"^\+?[\d\s\-]{7,15}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_fields(name=None, phone=None, email=None):
    if name is not None and not name.strip():
        raise ValueError("Name cannot be empty")
    if phone is not None and not PHONE_RE.match(phone.strip()):
        raise ValueError("Phone must be 7-15 digits (optional +, spaces, dashes)")
    if email is not None and email.strip() and not EMAIL_RE.match(email.strip()):
        raise ValueError("Email format is invalid")


class ContactManager:
    def __init__(self, path):
        self.path = path
        self.contacts = load_contacts(path)

    def _next_id(self):
        return max((c["id"] for c in self.contacts), default=0) + 1

    def _find(self, contact_id):
        for contact in self.contacts:
            if contact["id"] == contact_id:
                return contact
        raise KeyError(f"No contact with ID {contact_id}")

    def add(self, name, phone, email="", contact_id=None):
        validate_fields(name, phone, email)
        if contact_id is None:
            contact_id = self._next_id()
        elif any(c["id"] == contact_id for c in self.contacts):
            raise ValueError(f"ID {contact_id} already exists")
        contact = {"id": contact_id, "name": name.strip(),
                   "phone": phone.strip(), "email": email.strip()}
        self.contacts.append(contact)
        save_contacts(self.path, self.contacts)
        return contact

    def search(self, text):
        needle = text.strip().lower()
        return [c for c in self.contacts if needle in c["name"].lower()]

    def update(self, contact_id, name=None, phone=None, email=None):
        validate_fields(name, phone, email)
        contact = self._find(contact_id)
        updated = dict(contact)
        for field, value in (("name", name), ("phone", phone), ("email", email)):
            if value is not None:
                updated[field] = value.strip()
        contact.update(updated)
        save_contacts(self.path, self.contacts)
        return contact

    def delete(self, contact_id):
        contact = self._find(contact_id)
        self.contacts.remove(contact)
        save_contacts(self.path, self.contacts)
        return contact

    def list_all(self):
        return sorted(self.contacts, key=lambda c: c["id"])


MENU = """
--- Contact Manager ---
1. Add   2. Search   3. Update   4. Delete   5. List   0. Exit
"""


def _show(contacts):
    if not contacts:
        print("  (no contacts)")
    for c in contacts:
        print(f"  [{c['id']}] {c['name']} | {c['phone']} | {c['email'] or '-'}")


def _ask_id(prompt="Contact ID: "):
    try:
        return int(input(prompt).strip())
    except ValueError:
        raise ValueError("ID must be a whole number") from None


def main(path="contacts.json"):
    try:
        manager = ContactManager(path)
    except StorageError as exc:
        print("ERROR:", exc)
        return 1

    while True:
        print(MENU)
        choice = input("Choice: ").strip()
        try:
            if choice == "1":
                c = manager.add(input("Name: "), input("Phone: "), input("Email (optional): "))
                print("Added:"); _show([c])
            elif choice == "2":
                _show(manager.search(input("Search name: ")))
            elif choice == "3":
                cid = _ask_id()
                print("Leave blank to keep the current value.")
                name, phone, email = input("New name: "), input("New phone: "), input("New email: ")
                c = manager.update(cid, name or None, phone or None, email or None)
                print("Updated:"); _show([c])
            elif choice == "4":
                c = manager.delete(_ask_id())
                print("Deleted:"); _show([c])
            elif choice == "5":
                _show(manager.list_all())
            elif choice == "0":
                print("Goodbye!")
                return 0
            else:
                print("Please choose 0-5.")
        except (ValueError, KeyError) as exc:
            print("Error:", exc.args[0] if exc.args else exc)
        except OSError as exc:
            print("Could not save data:", exc)
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())