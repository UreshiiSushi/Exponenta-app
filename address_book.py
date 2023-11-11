# from _collections_abc import Iterator
import re
import pickle
from pathlib import Path
from itertools import islice
from collections import UserDict
from datetime import date, datetime

save_file = Path("phone_book.bin")

help_message = """Use next commands:
    <add> 'name' 'phone'  - add name and phone number to the dictionary
    <add_b> 'name' 'birthday' - add birthday date to the name in dictionary
    <add_phone> 'name' 'phone'  - add phone number to the name in dictionary
    <change> 'name' 'phone' 'new_phone' - change phone number for this name
    <days_to_birthday> 'name' - return number days to birhday
    <birthday> 'num' - return records with birthday date in 'num' days
    <delete> 'name' - delete name and phones from the dictionary
    <find> 'info' - find all records includes 'info' in Name or Phone
    <hello> - greeting
    <seek> 'name' 'phone' - find phone for name in the dictionary
    <phone> 'name' - show phone number for this name
    <remove_phone> 'name' 'phone' - remove phone for this name
    <show_all>  -  show all records in the dictionary
    <show_all> 'N' - show records by N records on page
    <exit> or <close> or <good_bye> - exit from module"""

greeting_message = """Welcome to Address Book.
Type command or 'help' for more information."""

class DateError(Exception):
    ...


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    ...


class Email(Field):
    def __init__(self, email: str):
        self.__email = None
        self.email = email

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, email):
        if re.match(r"[a-zA-Z][a-zA-Z0-9-_.]+\@[a-zA-Z]+\.[a-zA-Z][a-zA-Z]+", email):
            self.__email = email
        else:
            raise ValueError(
                "Wrong email format. Use pattern <name@domain.com> for email"
            )

    def __str__(self):
        return f"{self.__email}"


class Birthday(Field):
    # def __init__(self, bd: str):
    #     self.__birthday = None
    #     self.birthday = bd

    # @property
    # def birthday(self):
    #     return self.__birthday

    # @birthday.setter
    # def birthday(self, bd):
    #     if re.match(r"[0-9]{4}\-[0-9]{2}\-[0-9]{2}", bd):
    #         bd_date = list(map(int, bd.split("-")))
    #         birthday = date(*bd_date)
    #         # self.__birthday = birthday
    #         self.birthday = birthday
    #     else:
    #         raise ValueError("Wrong date format. Use YYYY-MM-DD")
    def __init__(self, birthday) -> None:
        self.__birthday = None
        self.birthday = birthday

    @property
    def birthday(self):
        return self.__birthday

    @birthday.setter
    def birthday(self, birthday):
        if isinstance(birthday, datetime):
            self.birthday = birthday
        else:
            raise DateError()

    def __str__(self):
        return f"Days to birthday: {self.days_to_birthday}"


class Phone(Field):
    def __init__(self, phone: str):
        self.__phone = None
        self.phone = phone

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, phone: str):
        if re.match(r"[0-9]{10}", phone):
            self.__phone = phone
        else:
            raise ValueError("Wrong phone format. It must contains 10 digits")


class Record:
    def __init__(self, name, phone: str = None, birthday_date: str = None, email=None):
        self.name = Name(name)
        self.phones: list(Phone) = []
        self.birthday = None
        if phone:
            self.phones.append(Phone(phone))
        if birthday_date:
            self.birthday = birthday_date  # Birthday(birthday_date)
        self.email = email

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
        return f"Added phone {phone} to contact {self.name}"

    def add_birthday(self, bd_date):  # str):
        self.birthday = bd_date  # Birthday(bd_date)

    def find_phone(self, phone: str):
        result = None
        for p in self.phones:
            if phone in p.phone:
                result = p
        return result

    def remove_phone(self, phone: str):
        search = self.find_phone(phone)
        if search in self.phones:
            self.phones.remove(search)
            return f"Removed phone {phone} from contact {self.name}."
        else:
            raise ValueError

    def edit_phone(self, phone: str, new_phone: str) -> str:
        edit_check = False
        for i in range(len(self.phones)):
            if self.phones[i].value == phone:
                edit_check = True
                self.phones[i] = Phone(new_phone)
                return f"Changed phone {phone} for contact {self.name} to {new_phone}"
        if not edit_check:
            raise ValueError

    def days_to_birthday(self) -> int:  # timedelta or str:
        if self.birthday:
            now_date = date.today()
            future_bd = self.birthday
            future_bd = future_bd.replace(year=now_date.year)
            if future_bd > now_date:
                return (future_bd - now_date).days
            else:
                future_bd = future_bd.replace(year=future_bd.year+1)
                return (future_bd - now_date).days
        else:
            raise DateError()
            # return f"No birthday set"

    def __str__(self):
        phones = "; ".join(p.phone for p in self.phones)
        return "Contact name: {}, birthday: {}, phones: {}".format(
            self.name, self.birthday, phones
        )


class AddressBook(UserDict):
    def __init__(self, data=None):
        super().__init__(data)
        self.counter = 0

    def add_record(self, rec: Record):
        if rec.name.value not in self.data.keys():
            self.data[rec.name.value] = rec
        else:
            raise ValueError

    def find(self, name: str):
        for k in self.data.keys():
            if name in k:
                return self.data.get(name)
        else:
            return None

    def delete(self, name: str):
        if name in self.data.keys():
            return self.data.pop(name)


    # def iterator(self, quantity: int = 1):
    #     values = list(map(str, islice(self.data.values(), None)))
    #     while self.counter < len(values):
    #         yield values[self.counter:self.counter+quantity]
    #         self.counter += quantity

    def iterator(self, quantity=None):
        self.counter = 0
        values = list(map(str, islice(self.data.values(), None)))
        while self.counter < len(values):
            if quantity:
                yield values[self.counter:self.counter+quantity]
                self.counter += quantity
            else:
                yield values  # [self.counter:self.counter+quantity]
                break

def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except TypeError:
            return "Not enough params. Try again"
        except KeyError:
            return "Unknown name. Try again"
        except ValueError:
            return "Wrong phone number. Try again"
        except DateError:
            return "Birthday date error or no birthday data"
    return inner

def greeting():
    return greeting_message

def help():
    return help_message


@input_error
def add_birhday(*args):
    name = args[0].lower()
    try:
        birhday = datetime.strptime(args[1], "%d/%m/%Y")
    except:
        raise DateError()
    rec = phone_book.get(name)
    if rec:
        rec.add_birthday(birhday.date())
        return f"{args[0].capitalize()}'s birthday added {args[1]}"
    else:
        raise DateError()


@input_error
def days_to_birthday(*args):
    name = args[0].lower()
    rec = phone_book.get(name)
    if rec:
        days = rec.days_to_birthday()
        return f"{days} days to {name.capitalize()}'s birthday"
    else:
        raise KeyError()


@input_error
def birthday_in(*args):
    num_days = int(args[0])
    for name in phone_book:
        rec = phone_book.get(name)
        try:
            days = rec.days_to_birthday()
            if days <= num_days:
                print(f"{rec} birthday in {days} days")
        except DateError:
            continue
    return f"Our birthday people in {num_days} days"
# save_file = Path("phone_book.bin")
# phone_book = AddressBook()

@input_error
def add_record(name: str, phone: str):
    global phone_book
    record = Record(name, phone)
    phone_book.add_record(record)
    # if not phone.isdecimal():
    #     raise ValueError
    # phone_book[name] = phone
    return f"{record}"


@input_error
def change_record(name: str, phone: str, new_phone: str):
    global phone_book
    rec: Record = phone_book.find(name)
    if rec:
        return rec.edit_phone(phone, new_phone)
    # if not new_phone.isdecimal():
    #     raise ValueError
    # rec = phone_book[name]
    # if rec:
    #     phone_book[name] = new_phone
    # return f"Changed phone {name=} {new_phone=}"


@input_error
def find(search: str) -> str or None:
    # global phone_book
    rec = []
    if search.isdigit():
        for k, v in phone_book.items():
            if v.find_phone(search):
                rec.append(phone_book[k])
    else:
        for k,v in phone_book.items():
            if search in k: 
                rec = phone_book[k]
    if rec:
        result = "\n".join(list(map(str, rec)))
        return f"Finded \n{result}"


def show_all():
    global phone_book
    for p in phone_book.iterator():
        input(">>>Press Enter for next record")
        print(p)


def save_book() -> str:
    global phone_book
    with open(save_file, "wb") as file:
        pickle.dump(phone_book, file)
    return f"Phonebook saved"


def load_book() -> str:
    global phone_book
    with open(save_file, "rb") as file:
        loaded_book = pickle.load(file)
    for k, v in loaded_book.items():
        phone_book.data[k] = v
    return f"Phonebook loaded"

# if all([save_file.exists(), save_file.stat().st_size> 0]):
#     print(load_book())


@input_error
def add_phone(*args):
    name = args[0].lower()
    new_phone = args[1]
    rec = phone_book.get(name)
    if rec:
        rec.add_phone(new_phone)
        return f"{args[0].capitalize()}'s phone added another one {args[1]}"
    else:
        raise KeyError()


@input_error
def add_record(name: str, phone: str):
    # global phone_book
    record = Record(name, phone)
    phone_book.add_record(record)
    # if not phone.isdecimal():
    #     raise ValueError
    # phone_book[name] = phone
    return f"{record}"


@input_error
def change_record(name: str, phone: str, new_phone: str):
    # global phone_book
    rec: Record = phone_book.find(name)
    if rec:
        return rec.edit_phone(phone, new_phone)
    # if not new_phone.isdecimal():
    #     raise ValueError
    # rec = phone_book[name]
    # if rec:
    #     phone_book[name] = new_phone
    # return f"Changed phone {name=} {new_phone=}"


@input_error
def find(search: str) -> str or None:
    # global phone_book
    rec = []
    if search.isdigit():
        for k, v in phone_book.items():
            if v.find_phone(search):
                rec.append(phone_book[k])
    else:
        for k, v in phone_book.items():
            if search in k:
                rec.append(phone_book[k])
                # rec = phone_book[k]
    if rec:
        result = "\n".join(list(map(str, rec)))
        return f"Finded \n{result}"
    else:
        return f'Nothing was found for your request.'


def show_all(*args):
    # for p in phone_book.iterator():
    #     print(p)
    #     input(">>>Press Enter for next record")
    try:
        if args[0]:
            for rec in phone_book.iterator(int(args[0])):
                print("\n".join([str(r) for r in rec]))
                input("Press Enter for next records")
    except:
        for rec in phone_book.iterator():
            print("\n".join([str(r) for r in rec]))


def save_book() -> str:
    # global phone_book
    with open(save_file, "wb") as file:
        pickle.dump(phone_book, file)
    return f"Phonebook saved"


def load_book() -> str:
    # global phone_book
    with open(save_file, "rb") as file:
        loaded_book = pickle.load(file)
    for k, v in loaded_book.items():
        phone_book.data[k] = v
    return f"Phonebook loaded"

def stop_command():
    ...

COMMANDS = {greeting: "hello",
            add_birhday: "add_b",
            add_record: "add",
            add_phone: "add_phone",
            birthday_in: "birthday",
            change_record: "change",
            days_to_birthday: "days_to_birthday",
            find: "find",
            help: "help",
            show_all: "show_all",
            save_book: "save",
            load_book: "load",
            stop_command: ("good_bye", "close", "exit")
            }

#TODO: implement addressbook_main()

def addressbook_main():
    ...

if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)
    bill_record = Record("Bill", "7234592343")
    dow_record = Record("Dow")
    book.add_record(bill_record)
    book.add_record(dow_record)
    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    for b in book.iterator(4):
        print(b)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    print(john)
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Додавання днів народження і вивід днів до нього
    john.add_birthday("1993-12-01")
    print(john.days_to_birthday())
    jane_record.add_birthday("2004-09-11")
    print(jane_record.days_to_birthday())
    print(dow_record.days_to_birthday())

    # Видалення запису Jane
    book.delete("Jane")

    # # Тест емейлу
    # letter_to = Email("asdf@domain.com")
    # print(letter_to)
