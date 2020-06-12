from django.urls import resolve
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from base.models import Testimonial, Investment, PropertyPicture, Remark, Client_Investment
from accounts.models import Client

import decimal


# Create your views here.


def home(request):
    testimonials = Testimonial.objects.all()
    return render(request, 'base/home.html', {'testimonials': testimonials})


def contact(request):
    return render(request, 'base/contacts.html')


def faq(request):
    return render(request, 'base/faq.html')


def about(request):
    return render(request, 'base/about-us.html')


def investments(request):
    invests = Investment.objects.all()
    context = {
        'investments': invests
    }
    return render(request, 'investments/investments.html', context)


def question_through_email(request):
    try:
        if request.method == 'POST':
            site_url = get_current_site(request)
            email = request.POST.get('email')
            user_query = request.POST.get('query')

            subject = "You've received messages from {}".format(email)
            message = ""
            email_from = settings.EMAIL_HOST_USER
            recipient_list = ['info@solomartel.com']
            msg_html = render_to_string('email/question_email.html',
                                        {'your_query': user_query, 'email': email, 'site_url': site_url})
            send_mail(subject, message, f'Solomartel Holdings<{email_from}>', recipient_list,
                      html_message=msg_html, fail_silently=False, )

            messages.success(request, 'Your question has been sent successfully')
        return redirect(reverse('base:investment', kwargs={'name': request.session['investment']}))

    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, str(e))
        return redirect(reverse('base:investment', kwargs={'name': request.session['investment']}))


def investment(request, name):
    context = {}
    try:
        investment_record = Investment.objects.get(name=name)
        context['investment_record'] = investment_record
        request.session['investment'] = name
        if request.user.is_authenticated:
            client = Client.objects.get(user=request.user)
            client_investment = Client_Investment.objects.get(client=client, investment=investment_record,
                                                              approved=True, deleted=False)
            percentage_invested = (client_investment.invested_amount*100)/investment_record.invested_amount
            context['client_investment'] = client_investment
            context['percentage_invested'] = percentage_invested
        # with_profile_pic = investment_record.my_images.all()[0]

        return render(request, 'investments/view_investment.html', context)
    except Investment.DoesNotExist:
        context['msg'] = 'Something went wrong, Please try again later'
        return render(request, 'investments/view_investment.html', context)
    except Client_Investment.DoesNotExist:
        import traceback
        traceback.print_exc()
        return render(request, 'investments/view_investment.html', context)
    except Client.DoesNotExist:
        return render(request, 'investments/view_investment.html', context)


def past_projects(request):
    context = {}
    try:
        return render(request, 'base/past_project.html')
    except:
        import traceback
        traceback.print_exc()
        context['msg'] = 'Something went wrong,Please try again later'
        return render(request, 'base/past_projects.html')


@login_required
def investment_form(request, invest):
    context = {}
    try:
        # get_id_of_investoment = request.GET.get('inverst_name')
        # investment_record = PropertyPicture.objects.get(investment_id=int(get_id_of_investoment))
        investment_record = Investment.objects.get(name=invest)
        # user_id = request.user.id
        client = Client.objects.get(user=request.user)

        context['investment_record'] = investment_record
        if request.method == 'POST':
            investmentamount = request.POST.get('investmentamount')
            phonenumber = request.POST.get('phonenumber')
            check_offer = Client_Investment.objects.filter(investment=investment_record, client=client, deleted=False)
            if check_offer:
                context['msg'] = 'Sorry, You already offer for this investment'
                return render(request, 'investments/invest_form.html', context)

            client_investment = Client_Investment.objects.create(
                investment=investment_record, invested_amount=decimal.Decimal(investmentamount),
                phone_number=phonenumber,
                client=client, status='Pending')

            investment_record.invested_amount += decimal.Decimal(investmentamount)
            investment_record.save()
            context[
                'success_msg'] = 'Thank you for your registration ! Your offer has been successfully created,Enter your details to Compelete payment process'
            return redirect(reverse('base:choose_payment', kwargs={'invest': client_investment.id}))
        # context['get_id_of_investoment'] = invest
        return render(request, 'investments/invest_form.html', context)
    except Investment.DoesNotExist:
        context['msg'] = 'Unrecognized investment'
        return render(request, 'investments/invest_form.html', context)
    except:
        import traceback
        traceback.print_exc()
        context['msg'] = 'Something went wrong,Please try again later'
        return render(request, 'investments/invest_form.html', context)


@login_required
def choose_payment(request, invest):
    context = {}
    try:
        context['id_offer_obj'] = invest
        return render(request, 'investments/payment_way.html', context)
    except:
        import traceback
        traceback.print_exc()
        context['msg'] = 'Something went wrong,Please try again later'
        return render(request, 'investments/payment_way.html')


@login_required
def my_transactions(request):
    context = {}
    try:
        # request_user = request.user.id
        client = Client.objects.get(user=request.user)
        transactions = Client_Investment.objects.filter(client=client, deleted=False)
        context['all_transactions'] = transactions
        return render(request, 'investments/my_transactions.html', context)
    except:
        import traceback
        traceback.print_exc()
        return render(request, 'investments/my_transactions.html')


@login_required
def my_investments(request):
    try:
        # request_user = request.user.id
        client = Client.objects.get(user=request.user)
        investments = Client_Investment.objects.filter(client=client, done=True, approved=True, deleted=False)
        context = {'transactions': investments}
        return render(request, 'investments/my_investments.html', context)
    except:
        import traceback
        traceback.print_exc()
        return render(request, 'investments/my_investments.html')


@login_required
def delete_investment(request, id):
    try:
        transaction_to_delete = Client_Investment.objects.get(id=id)
        if not transaction_to_delete.approved:
            transaction_to_delete.deleted = True
    except Client_Investment.DoesNotExist:
        import traceback
        traceback.print_exc()

    return redirect(reverse('base:my_transactions'))
