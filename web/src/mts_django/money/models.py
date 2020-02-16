from datetime import datetime
from decimal import Decimal
from django.db import models
from django.db.models import Q
from users.models import User

class Currency(models.Model):
    class Meta:
        indexes = [models.Index(fields=['name', ])]
    name = models.CharField(max_length=32, unique=True, null=False)

class Course(models.Model):
    class Meta:
        constraints = [models.UniqueConstraint(fields=['base_currency', 'currency', 'date'], name='unique__base_currency__currency___date')]
    currency = models.ForeignKey(Currency, related_name='currency', null=False, on_delete = models.CASCADE)  
    base_currency = models.ForeignKey(Currency, related_name='base_currency', null=False, on_delete = models.CASCADE)  
    course = models.DecimalField(max_digits=18, decimal_places=4, null=False)
    date = models.DateTimeField()
    @classmethod
    def create(cls, currency, base_currency, course, date):
        new_rate = cls(currency=currency, base_currency=base_currency, course=course, date=date)
        return new_rate

class Account(models.Model):
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'currency'], name='unique_user_and_currency'),]
        indexes = [models.Index(fields=('user',))]
    user = models.ForeignKey(User, related_name='accounts', null=False, on_delete=models.PROTECT)
    currency = models.ForeignKey(Currency, null=False, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=18, decimal_places=4, null=False, default=0)
    created = models.DateTimeField(auto_now_add=True)
    @classmethod
    def create(cls, user, currency, balance):
        account = cls(user=user, currency=currency, balance=balance)
        return account

class Transfer(models.Model):
    class Meta:
        indexes = [models.Index(fields=['sender_account', ])]
    sender_account = models.ForeignKey(Account, related_name='sender_account', null=False, on_delete=models.PROTECT)
    receiver_account = models.ForeignKey(Account, related_name='receiver_account', null=False, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=18, decimal_places=4, null=False)
    created = models.DateTimeField(auto_now_add=True)
    @classmethod
    def create(cls, sender_acc, receiver_acc, amount):
        transfer = cls(sender_account=sender_acc, receiver_account=receiver_acc, amount=amount)
        return transfer

def convert_amount(currency_from: Currency, currency_to: Currency, amount: Decimal, date=datetime.now()) -> Decimal:
    """Function for convertation money from one currency to anoter using rates of courses from database
    
    :param currency_from: source currency may be of types str of Currency model
    :param currency_to: destination currency may be of types str of Currency model
    :param amount: amount of money of currency_from
    :param date: date of courses
    :returns: converted amount
    """
    if isinstance(currency_from, Currency):
        course_list_from = Course.objects.filter(Q(currency=currency_from)&Q(date__lt=date)).order_by('-date')
    elif isinstance(currency_from, str):
        course_list_from = Course.objects.filter(Q(currency__name=currency_from)&Q(date__lt=date)).order_by('-date')
    if course_list_from:
        course_from = course_list_from[0].course
    else:
        course_list_from = Course.objects.filter(Q(base_currency__name=currency_from)&Q(date__lt=date)).order_by('-date')
        if course_list_from:
            course_from = 1
        else:
            raise Exception('There is no course for the currency %s on date %s' % (currency_from, date))
    if isinstance(currency_to, Currency):
        course_list_to = Course.objects.filter(Q(currency=currency_to)&Q(date__lt=date)).order_by('-date')
    elif isinstance(currency_to, str):
        course_list_to = Course.objects.filter(Q(currency__name=currency_to)&Q(date__lt=date)).order_by('-date')
    if course_list_to:
        course_to = course_list_to[0].course
    else:
        course_list_to = Course.objects.filter(Q(base_currency=currency_to)&Q(date__lt=date)).order_by('-date')
        if course_list_to:
            course_to = 1
        else:
            raise Exception('There is no course for the currency %s on date %s' % (currency_to, date))
    return (course_from, course_to, course_to/course_from * Decimal(amount))




