from django.shortcuts import  get_object_or_404, render, redirect
from wallet.models import Wallet, EasyPay, Referral
from django.db.models import Q
from django.contrib import messages
import shortuuid
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.





@login_required(login_url='userauths:sign-in')
def wallet_view(request):
    if request.user.is_superuser:
         return redirect('admin_side:dashboard')
    try:
        easy = EasyPay.objects.get(user=request.user)
        wallet = Wallet.objects.filter(user=request.user, easypay=easy).order_by('-created_at')
    except ObjectDoesNotExist:
        easy = None
        wallet = None
    context = {
        'wallet': wallet,
        'easy':easy,
    }
    return render(request, 'user/dashboard/wallet.html', context)


@login_required(login_url='userauths:sign-in')
def credit(amount, order_item, user):
    print('hi')
    try:
        amount = amount
        order_item = order_item
        easy, check = EasyPay.objects.get_or_create(user = user)
        print('in the has attri checking')
        Wallet.objects.get_or_create(
            user = user,
            easypay = easy,
            payment = order_item.payment_details,
            order_id = order_item.order.order_number,
            order_item = order_item,
            amount = amount,
            is_debit = False,
        )
        easy.balance +=amount
        easy.save()

    except Exception as e:
        print(f'the error is that which is {e}')


@login_required(login_url='userauths:sign-in')
def easypay(total, order, user):
    easy = get_object_or_404(EasyPay, user=user)
    if easy.balance < total:
        return False  # Not enough balance

    easy.balance -= total
    easy.save()

    Wallet.objects.get_or_create(
        user=user,
        easypay=easy,
        payment=order.payment_details,
        order_id=order.order_number,
        amount=total,
        is_debit=True,
    )
    return True


            

        