class TicketException(Exception):
    pass

class TicketNotFoundException(TicketException):
    pass

class TicketInvalidIDException(TicketException):
    pass

class TicketInvalidStatusException(TicketException):
    pass
