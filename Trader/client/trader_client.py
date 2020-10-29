from abc import ABC


class TraderClient(ABC):
    def onlinePayment(self, a, b):
        pass


class TraderRequest(ABC):
    pass


class TraderResponse(ABC):
    pass


class InvalidLoginException(Exception):
    pass


class PaymentErrorException(Exception):
    pass
