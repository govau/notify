import abc


class SMSClient(abc.ABC):
    '''
    Base Sms client for sending SMSs.
    '''

    @abc.abstractmethod
    def send_sms(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_name(self):
        pass


class PollableSMSClient(SMSClient):
    @abc.abstractmethod
    def check_message_status(self, reference, **options):
        pass
