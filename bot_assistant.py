from collections import deque, UserDict
from datetime import datetime


DATE_FORMAT = "%d.%m.%Y"
N = 2


class AddressBook(UserDict):
    def iterator(self):
        return AddressBookIterator(self)

    def add_record(self, *args):
        name_key, phone_key, birthday_key = tuple(args[1:4])
        name = args[name_key+1]
        for key in self.data.keys():
            if key.casefold() == name.casefold():
                if not phone_key and not birthday_key:
                    return "The contact is exist"
                else:
                    if phone_key:
                        for phone in map(Phone, args[phone_key+1:birthday_key if birthday_key else len(args)]):
                            self.data[key].add_phone(phone)
                    if birthday_key:
                        self.data[key].set_birthday(Birthday(args[-1]))
                    return "Add data in record success"
        name = Name(name.title())
        if not name:
            return "The name is invalid"
        if phone_key and birthday_key:
            record = Record(name, *map(Phone, args[phone_key+1:birthday_key]), birthday=Birthday(args[-1]))
        elif phone_key and not birthday_key:
            record = Record(name, *map(Phone, args[phone_key+1:len(args)]))
        elif not phone_key and birthday_key:
            record = Record(name, birthday=Birthday(args[-1]))
        else:
            record = Record(name)
        self.data[record.name.value] = record
        return "Add record success"
    
    def change_record(self, *args):
        len_args = len(args)
        name_key, phone_key, birthday_key = tuple(args[1:4])
        name = args[name_key+1]
        new_name = None
        if len_args - name_key != 2 and not args[name_key+2].startswith("-"):
            new_name = args[name_key+2]
            if name == new_name:
                return "Old and new names should be different"
            for key in self.data.keys():
                if key.casefold() == new_name.casefold():
                    return "The new contact is already exist"
        for key in self.data.keys():
            if key.casefold() == name.casefold():
                if new_name:
                    new_name = Name(new_name.title())
                    if not new_name:
                        return "The new name is invalid"
                    old_record = self.data.pop(key)
                    record = Record(new_name, *old_record.phones, birthday=old_record.birthday[0] if old_record.birthday else None)
                    key = record.name.value
                    self.data[key] = record
                if phone_key:
                    for el in enumerate(args[phone_key+1:birthday_key if birthday_key else len_args]):
                        if not el[0] % 2:
                            self.data[key].change_phone(Phone(args[el[0]+phone_key+1]), Phone(args[el[0]+phone_key+2]))
                if birthday_key:
                    self.data[key].set_birthday(Birthday(args[-1]))
                return "Change record success"
        return "The contact is not found"
    
    def remove_record(self, *args):
        name_key, phone_key, birthday_key = tuple(args[1:4])
        name = args[name_key+1]
        for key in self.data.keys():
            if key.casefold() == name.casefold():
                if not phone_key and not birthday_key:
                    self.data.pop(key)
                    return "Remove record success"
                else:
                    if phone_key:
                        phone_args = args[phone_key+1:birthday_key if birthday_key else len(args)]
                        if phone_args:
                            for phone in map(Phone, phone_args):
                                self.data[key].remove_phone(phone)
                        else:
                            self.data[key].phones.clear()
                    if birthday_key:
                        self.data[key].birthday.clear()
                    return "Remove data in record success"
    
    def show(self, *args):
        if not self.data:
            result = "The address book is empty"
        elif args[1] == "all":
            result = ""
            for key, value in self.items():
                result += f"Name: {key}\n"
                if value.phones:
                    result += f"    Phone(s): {', '.join(map(str, value.phones))}\n"
                else:
                    result += f"    Phone(s):\n"
                if value.birthday:
                    result += f"    Birthday: {value.birthday[0]}, {value.days_to_birthday()} day(s) to next birthday\n"
                else:
                    result += f"    Birthday:\n"
                result += "\n"
        else:
            result = ""
            name_key, phone_key = tuple(args[1:3])
            name_string = args[name_key+1] if name_key else None
            phone_string = args[phone_key+1] if phone_key else None
            for key, value in self.items():
                found_in_phones = False
                if phone_key:
                    for phone in value.phones:
                        if phone_string in phone.value:
                            found_in_phones = True
                            break
                if (name_string and name_string.casefold() in key.casefold()) or found_in_phones:
                    result += f"Name: {key}\n"
                    if value.phones:
                        result += f"    Phone(s): {', '.join(map(str, value.phones))}\n"
                    else:
                        result += f"    Phone(s):\n"
                    if value.birthday:
                        result += f"    Birthday: {value.birthday[0]}, {value.days_to_birthday()} day(s) to next birthday\n"
                    else:
                        result += f"    Birthday:\n"
                    result += "\n"
        return result


class AddressBookIterator:
    def __init__(self, address_book: AddressBook):
        self.address_book = address_book
        self.keys = []
        for key in self.address_book.keys():
            self.keys.append(key)
        self.len_keys = len(self.keys)

    def __iter__(self):
        self.current_index = 0
        return self
    
    def __next__(self):
        if self.current_index >= self.len_keys:
            raise StopIteration
        result = ""        
        for _ in range(N):
            key = self.keys[self.current_index]
            value = self.address_book[key]
            result += f"Name: {key}\n"
            if value.phones:
                result += f"    Phone(s): {', '.join(map(str, value.phones))}\n"
            else:
                result += f"    Phone(s):\n"
            if value.birthday:
                result += f"    Birthday: {value.birthday[0]}, {value.days_to_birthday()} day(s) to next birthday\n"
            else:
                result += f"    Birthday:\n"
            result += "\n"
            self.current_index += 1
            if self.current_index >= self.len_keys:
                break
        return result

class Record:
    def __init__(self, name, *phones, birthday=None):
        self.name = name
        self.phones = []
        self.birthday = deque(maxlen=1)
        for phone in phones:
            self.add_phone(phone)
        if birthday:
            self.set_birthday(birthday)

    def days_to_birthday(self):
        today = datetime.now().date()
        timedelta = self.birthday[0].value.replace(year=today.year) - today
        if timedelta.days < 0:
            timedelta = self.birthday[0].value.replace(year=today.year+1) - today
        return timedelta.days

    def add_phone(self, phone):
        for item in self.phones:
            if item == phone:
                return "The phone is exist"
        if phone:
            self.phones.append(phone)
        return "Add phone success"

    def change_phone(self, phone, new_phone):
        if phone == new_phone:
            return "Old and new phones should be different"
        for item in self.phones:
            if item == new_phone:
                return "The new phone is already exist"
        for i, item in enumerate(self.phones):
            if item == phone:
                if new_phone:
                    self.phones[i] = new_phone
                    return "Change success"
        return "The phone is not found"

    def remove_phone(self, phone):
        for item in self.phones:
            if item == phone:
                self.phones.remove(phone)
                return "Remove phone success"
        return "The phone is not found"
    
    def set_birthday(self, birthday):
        self.birthday.append(birthday)
        return "Set birthday success"


class Field:
    def __bool__(self):
        return bool(self.value)
    
    def __str__(self):
        return str(self.value)
    
    def __eq__(self, other):
        return self.value == other.value
        

class Birthday(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self):
        return self.value.strftime(DATE_FORMAT)

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, DATE_FORMAT).date()
        except ValueError:
            pass


class Name(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if value.isalpha():
            self.__value = value.title()


class Phone(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if value.isdecimal() and len(value) == 12:
            self.__value = value


def error(message):
    return message


def exit():
    return "Good bye!"


def hello():
    return "Can I help you?"


def no_command():
    return "Unknown command"


def parser(text: str) -> tuple[callable, tuple[str]|None]:
    args = text.strip().split()
    arg0 = args[0].casefold()
    if not args or (arg0 not in ("add", "change", "remove", "show") \
    and text.strip().casefold() not in ("show all", "good bye", "bye", "close", "exit", "hello")):
        return no_command, None
    if text.strip().casefold() == "show all":
        return AddressBook.show, args
    name_key = None
    phone_key = None
    birthday_key = None
    for i, arg in enumerate(args):
        arg = arg.casefold()
        if arg == "-name" or arg == "-names":
            if name_key:
                return error, "There are shouldn't be duplicate keys"
            else:
                name_key = i
        if arg == "-phone" or arg == "-phones":
            if phone_key:
                return error, "There are shouldn't be duplicate keys"
            else:
                phone_key = i
        if arg == "-birthday":
            if birthday_key:
                return error, "There are shouldn't be duplicate keys"
            else:
                birthday_key = i

    if arg0 == "add" or arg0 == "change" or arg0 == "remove":
        if not name_key:
            return error, "The -name(s) key is necessary for adding, changing or removing"
        if (birthday_key and phone_key and (birthday_key < name_key or birthday_key < phone_key)) or (phone_key and phone_key < name_key):
            return error, "The order of keys for adding, changing or removing should be: -name(s) -phone(s) -birthday"
    elif arg0 == "show":
        if name_key and phone_key and phone_key < name_key:
            return error, "The order of keys for showing should be: -name(s) -phone(s)"
        if birthday_key:
            return error, "Showing by birthday are not allowed"
        
    if arg0 == "add" or arg0 == "change" or arg0 == "remove" or arg0 == "show":
        if name_key:
            name_key += 3
        if phone_key:
            phone_key += 3
        if birthday_key:
            birthday_key += 3
        args.insert(1, birthday_key)
        args.insert(1, phone_key)
        args.insert(1, name_key)
        len_args = len(args)
        
    if arg0 == "add":
        if birthday_key and len_args - birthday_key != 2:
            return error, "There is should be single birthday value"
        if phone_key:
            number_of_phones = birthday_key - phone_key - 1 if birthday_key else len_args - phone_key - 1
            if number_of_phones == 0:
                return error, "There is should be at least one phone"
        if (phone_key and phone_key - name_key != 2) or (not phone_key and birthday_key and birthday_key - name_key != 2) \
        or (not phone_key and not birthday_key and len_args - name_key != 2):
            return error, "There is should be single name"
        return AddressBook.add_record, args
    elif arg0 == "change":
        if birthday_key and len_args - birthday_key != 2:
            return error, "There is should be single birthday value"
        if phone_key:
            number_of_phones = birthday_key - phone_key - 1 if birthday_key else len_args - phone_key - 1
            if number_of_phones == 0 or number_of_phones % 2:
                return error, "There are should be even number of phones"
        if (phone_key and phone_key - name_key not in (2, 3)) or (not phone_key and birthday_key and birthday_key - name_key not in (2, 3)) \
        or (not phone_key and not birthday_key and len_args - name_key not in (2, 3)):
            return error, "There are should be one or two names"
        return AddressBook.change_record, args
    elif arg0 == "remove":
        if birthday_key and len_args - birthday_key != 1:
            return error, "There is shouldn't be birthday value, just key"
        if (phone_key and phone_key - name_key != 2) or (not phone_key and birthday_key and birthday_key - name_key != 2) \
        or (not phone_key and not birthday_key and len_args - name_key != 2):
            return error, "There is should be single name"
        return AddressBook.remove_record, args
    elif text.strip().casefold() == "good bye" or text.strip().casefold() == "bye" or text.strip().casefold() == "close" or text.strip().casefold() == "exit":
        return exit, None
    elif text.strip().casefold() == "hello":
        return hello, None
    elif arg0 == "show":
        if not name_key and not phone_key:
            return error, "There is should be at least one key"
        if name_key and ((phone_key and phone_key - name_key != 2) or (not phone_key and len_args - name_key != 2)):
            return error, "There is should be single name"
        if phone_key and len_args - phone_key != 2:
            return error, "There is should be single phone"
        return AddressBook.show, args


def main():
    address_book = AddressBook()
    while True:
        user_input = input(">>> ")
        command, data = parser(user_input)
        type_data = type(data)
        if type_data == list:
            result = command(address_book, *data)
        elif type_data == str:
            result = command(data)
        else:
            result = command()
        print(result)
        if result == "Good bye!":
            break
    
    for i, record in enumerate(address_book.iterator()):
        print(f"\nPage {i+1}\n")
        print(record)


if __name__ == "__main__":
    main()