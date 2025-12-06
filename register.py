from abc import ABC, abstractmethod

class user:
    def _init_ (self, name, age, contact, address, ):
        self._name = name
        self._age = age
        self._address = address
        self._contact = contact

    @abstractmethod
    def get_type(self):
        pass

    # Encapsulation (getters)
    def name(self): return self._name
    def age(self): return self._age
    def address(self): return self._address
    def contact(self): return self._contact

class student(user):
    def __init__(self, name, age, contact, address, sr_code):
        super().__init__(name, age, contact, address)
        self.sr_code = sr_code

    def get_type(self):
        return "student"
    
class prof(user):
    def __init__(self, name, age, contact, address, department ):
        super().__init__(name, age, contact, address)
        self.department = department

    def get_type(self):
        return "prof"
    
class worker(user):
    def __init__(self, name, age, contact, address, work_type):
        super().__init__(name, age, contact, address)
        self.work_type = work_type

    def get_type(self):
        return "worker"
    
class parent(user):
    def __init__(self, name, age, contact, address):
        super().__init__(name, age, contact, address)

    def get_type(self):
        return "parent"