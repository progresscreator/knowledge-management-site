# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.sites.models import Site

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail


from iknow.forms import QuestionForm, AnswerForm
from iknow.models import Question, Answer, Thumb, QuestionTag, Rating
from iknow.models import QuestionComment, AnswerComment, QuestionAmendment
from iknow.models import AnswerTip
from iknow import utils
from egghead.models import get_egghead_from_user, EggHead
from worldbank.models import Transaction, FreezeCredit
from worldbank.utils import worldbank_subsidize
from mysearch.utils import search_questions
from tribes.models import Tribe
from core.utils import sms_notify_list, verified_emails, verified_phones
import core.utils

# Python libraries
import os
import logging
from datetime import datetime
from datetime import timedelta
import simplejson

klogger = logging.getLogger("pwe.iknow")

@login_required
def iknow_home(request, template="iknow/iknow_home.html"):
    # for question in Question.objects.filter(status__in=("A","E","P")):
    #    question.update_time()
    my_questions = Question.objects.filter(status__in=("A","E","P"), asker=request.user)\
                    .order_by("-time_stamp")
    egghead = get_egghead_from_user(request.user)
    top_eggheads = EggHead.objects.order_by("-wealth_notes")[:10]
    top_eggheads_earning = EggHead.objects.order_by("-earning_total")[:10]
    top_tags = QuestionTag.objects.order_by("-count")[:10]
    tribes = Tribe.objects.filter(members=request.user)
    return render_to_response(template, 
                {"egghead": egghead,
                 "top_eggheads": top_eggheads,
                 "top_eggheads_earning": top_eggheads_earning, 
                 "top_tags": top_tags,
                 "tribes": tribes,
                 "my_questions": my_questions,
                 },
                context_instance=RequestContext(request))

@login_required
def iknow_tags(request, template="iknow/iknow_tags.html"):
    return render_to_response(template, 
                context_instance=RequestContext(request))

@login_required
def iknow_tag(request, tag_id, template="iknow/iknow_tag.html"):
    try:
        tag = QuestionTag.objects.get(pk=tag_id)
    except Exception, e:
        tag = QuestionTag.objects.all()[0]
    return render_to_response(template, 
                {"tag": tag,
                },
                context_instance=RequestContext(request))

@login_required
def iknow_ask(request, template="iknow/iknow_ask.html"):
    form_error = []
    egghead = get_egghead_from_user(request.user)
    tribes = request.user.tribes.all()
    if request.method == "POST":
        try:
            form = QuestionForm(request.POST)
        except IOError, e:
            klogger.warning("iknow_ask reading request.POST: %s" % e)
            return HttpResponseServerError
        if form.is_valid():
            question = Question()
            question.asker = request.user
            question.time_stamp = datetime.now()
            question.question_title = form.cleaned_data["title"]
            question.question_text = form.cleaned_data["details"]
            question.points_offered = form.cleaned_data["points_offered"]
            question.anonymous = form.cleaned_data["anonymous"]
            question.hide_answers = form.cleaned_data["hide_answers"]
            end_date = form.cleaned_data["end_date"]
            if question.points_offered > 0:
                question.points_expiration = datetime(end_date.year, end_date.month, end_date.day,
                    int(form.cleaned_data["end_hour"]), 0, 0, 0)
            else:
                question.points_expiration = question.time_stamp + timedelta(days=7)
            tags = form.cleaned_data["tags"]
            cleaned_tags = []
            for tag in tags.split(","):
                cleaned_tag = utils.clean_tag(tag)
                if cleaned_tag:
                    cleaned_tags.append(cleaned_tag)
                    tag_obj, created = QuestionTag.objects.get_or_create(name=cleaned_tag)
                    if not created: 
                        tag_obj.update_count()
            if cleaned_tags:
                question.tags = ", ".join(cleaned_tags)
            question.save()
            for key in request.POST:
                if key.startswith("tribeshare"):
                    tribe = Tribe.objects.get(pk=key.split("_")[1])
                    question.to_groups.add(tribe)
                if key.startswith("tribeemail"):
                    tribe = Tribe.objects.get(pk=key.split("_")[1])
            if question.points_offered > 0:
                freezecredit = FreezeCredit(time_stamp=datetime.now(), fuser=request.user, ftype="F",
                    app="K", ttype="QA", amount=question.points_offered, question=question, cleared=False)
                freezecredit.save()

            # Reward 25 points if this is the asker's first question
            if request.user.questions_asked.count() == 1:
                worldbank_subsidize(question.asker, "KFQ", question)
                
            # Send a short message to users who subscribe, right now it's just a hack for Andy and me
            # To be fixed
            try:
                #recipients = ("5083188816", "6179092101", "6179011065")
                recipients = User.objects.filter(settings__new_q_notification_txt=True)\
                    .exclude(username=question.asker.username)
                phone_numbers = verified_phones(recipients)
                question_body = (question.question_title + " - " + question.question_text.replace("\n", " "))[:110]
                message = "Barter: " + question_body + " (prefix '" + str(question.id) + "' to your answer)"
                sms_notify_list(phone_numbers, message)
            except Exception, e:
                klogger.info(e)

            try:
                recipients = User.objects.filter(settings__new_q_notification_email=True)\
                    .exclude(username=question.asker.username)
                current_site = Site.objects.get_current()
                subject = u"[ %s ] %s" % (current_site.name, _("A new question entered the market"))
                t = loader.get_template("iknow/new_question.txt")
                c = Context({
                        "question": question,
                        "current_site": current_site,
                    })
                message = t.render(c)
                from_email = settings.DEFAULT_FROM_EMAIL
                send_mail(subject, message, from_email, verified_emails(recipients))
            except Exception, e:
                klogger.info(e)

            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = QuestionForm()
    average_price = Question.objects.aggregate(Avg("points_offered"))["points_offered__avg"]
    if not average_price: average_price = 0
    return render_to_response(template, 
                {"form": form,
                 "form_error": form_error,
                 "av_credits": egghead.available_credits(),
                 "balance": egghead.wealth_notes,
                 "av_price": "%.2f" % average_price,
                 "tribes": tribes,
                },
                context_instance=RequestContext(request))

@login_required
def iknow_my_questions(request, template="iknow/iknow_my_questions.html"):
    return HttpResponse("Myquestions")

@login_required
def iknow_questions(request, template="iknow/iknow_questions.html"):
    objs = Question.objects.all()
    return render_to_response(template, 
                {"objs": objs,},
                context_instance=RequestContext(request))

@login_required
def iknow_question(request, question_id, template="iknow/iknow_question.html"):
    # question = Question.objects.get(pk=question_id)
    question = get_object_or_404(Question, pk=question_id)
    question.update_time()
    answers = question.get_answers(standard="thumbs")    
    try:
        my_answer = Answer.objects.get(answerer=request.user, question=question)
        is_answered = True
        answer_form = AnswerForm(instance=my_answer)
    except:
        is_answered = False
        answer_form = AnswerForm()
    question.update_visits()
    if question.tags:
        results = search_questions(question.tags)
    else:
        results = search_questions(question.question_title)
    # results = results.exclude(index_pk=question.id)[:10]
    amendments = question.questionamendment_set.order_by("time_stamp")
    question_comments = question.questioncomment_set.order_by("-time_stamp")
    return render_to_response(template, 
                {"question": question,
                 "answer_form": answer_form,
                 "amendments": amendments,
                 "answers": answers,
                 "is_answered": is_answered,
                 "results": results,
                 "is_my_favorite": get_egghead_from_user(request.user).has_question_as_favorite(question),
                 "question_comments": question_comments,
                },
                context_instance=RequestContext(request))

@login_required
def iknow_question_extend(request, question_id):
    if request.method == "POST":
        question = Question.objects.get(pk=question_id)
        if question.rewarding() and question.status == "P":
            question.extend_expiration(7)
            return HttpResponse("0")
        else:
            return HttpResponse("1")
    else:
        klogger.debug("iknow_question_extend received a non-POST request")

@login_required
def iknow_question_moneyback(request, question_id):
    if request.method == "POST":
        question = Question.objects.get(pk=question_id)
        if question.rewarding() and question.answer_count() == 0:
            try: 
                freezecredit = FreezeCredit.objects.get(fuser=request.user, ftype="F", question=question)
                freezecredit.unfreeze()
                question.status = "U"
                question.save()
                return HttpResponse("0")
            except Exception, e:
                klogger.debug(e)
        else:
            return HttpResponse("1")
    else:
        klogger.debug("iknow_question_moneyback received a non-POST request")

@login_required
def iknow_question_al(request, question_id):
    if request.method == "POST":
        question = Question.objects.get(pk=question_id)
        points_offered = question.points_offered
        answers = []
        sum = 0
        for key in request.POST:
            answer_id = key.split("_")[1]
            answer = Answer.objects.get(pk=answer_id)
            answer.points_received = int(request.POST[key])
            sum = sum + answer.points_received
            answers.append(answer)
        if sum == points_offered:
            # Allocation is correctly done
            for answer in answers:
                answer.save()
            question.status = "S"
            question.save()
            try: 
                freezecredit = FreezeCredit.objects.get(fuser=request.user, ftype="F", question=question)
                freezecredit.unfreeze()
                for answer in answers:
                    transaction = Transaction(time_stamp=datetime.now(), flow_type="I", src=question.asker,
                        dst=answer.answerer, app="K", ttype="QA", amount=answer.points_received, question=question)
                    transaction.save()
                    transaction.execute()

                    recipients = (answer.answerer, )
                    current_site = Site.objects.get_current()

                    subject = u"[ %s ] %s" % (current_site.name, _("Your answer received %(points_received)d points!") % {
                            "points_received": answer.points_received,
                        })

                    t = loader.get_template("iknow/answer_points_received.txt")
                    c = Context({
                            "answer": answer,
                            "current_site": current_site,
                        })
                    send_mail(subject, t.render(c), settings.DEFAULT_FROM_EMAIL, verified_emails(recipients))
                asker_award = int(1.0*sum/4)
                worldbank_subsidize(question.asker, "AL", question, points=asker_award)
                return HttpResponse("0_%d" % asker_award)
            except Exception, e:
                print e
                klogger.warning(e)
                return HttpResponse("2")
        else:
            # Allocation is wrong
            for answer in answers:
                answer.points_received = 0
                answer.save()
            return HttpResponse("1")
            
@login_required
def iknow_answer(request, question_id, template="iknow/iknow_answer.html"):
    question = Question.objects.get(pk=question_id)
    if request.method == "POST":
        try:
            my_answer = Answer.objects.get(answerer=request.user, question=question)
            editing = True
            form = AnswerForm(request.POST, request.FILES, instance=my_answer)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.edit_time_stamp = datetime.now()
                answer.save()
                return HttpResponseRedirect(reverse("iknow_question", kwargs={"question_id": question.id}))
        except:
            editing = False
            form = AnswerForm(request.POST, request.FILES)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.answerer = request.user
                answer.question = question
                answer.time_stamp = datetime.now()
                answer.save()
                try:
                    current_site = Site.objects.get_current()

                    subject = u"[ %s ] %s" % (current_site.name, _("Your question received on answer from %(answerer_name)s") % {
                        "answerer_name": answer.display_name()
                    })

                    t = loader.get_template("iknow/receive_answer_message.txt")
                    c = Context({
                            "question": question,
                            "answer":answer,
                            "current_site": current_site,
                        })
                    message = t.render(c)
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to_email = verified_emails([question.asker])
                    send_mail(subject, message, from_email, to_email)
                except Exception, e:
                    klogger.info(e)

                return HttpResponseRedirect(reverse("iknow_question", kwargs={"question_id": question.id}))
    else:
        form = AnswerForm()

    return render_to_response(template, 
                {"obj": question,
                 "form": form,},
                context_instance=RequestContext(request))

def iknow_ajax_questions_fav(request, tribe_id, tag_id, template):
    title = _("Questions you have bookmarked")
    fqs = get_egghead_from_user(request.user).favorite_questions()
    if not tribe_id:
        fqs = fqs.filter(question__to_groups=None)
    else:
        tribe = Tribe.objects.get(pk=tribe_id)
        fqs = fqs.filter(question__to_groups=tribe)
    if tag_id:
        tag = QuestionTag.objects.get(pk=tag_id)
        fqs = fqs.filter(question__tags__icontains=tag.name)
    if not fqs:
        return render_to_response(template, 
                    {"objs": None,
                     "title": title,
                     "order": "time", 
                     "page": 0,
                     "total_pages": 0,
                     "qtype": "my_favorite",
                     "home": False,
                     },
                    context_instance=RequestContext(request))
    order = "time"
    page = 1
    if request.method == "POST":
        if request.POST.has_key("order"):
            order = request.POST["order"]
        if request.POST.has_key("page"):
            page = int(request.POST["page"])
    if order == "time":
        fqs_ordered = fqs.order_by("-question__time_stamp")
    paginator = Paginator(fqs_ordered, 20)
    return render_to_response(template, 
                {"objs": {"object_list": [fq.question for fq in paginator.page(page).object_list]},
                 "title": title,
                 "order": order, 
                 "page": page,
                 "total_pages": paginator.num_pages,
                 "qtype": "my_favorite",
                 "home": False,
                 },
                context_instance=RequestContext(request))
    
@login_required
def iknow_ajax_question_comments(request, question_id, template="iknow/iknow_ajax_question_comments.html"):
    question = Question.objects.get(pk=question_id)
    page = 1
    if request.method == "GET":
        if request.GET.has_key("page"):
            page = int(request.GET["page"])
    comments = question.questioncomment_set.order_by("-time_stamp")
    paginator = Paginator(comments, 10)
    return render_to_response(template, 
                {"objs":paginator.page(page),
                 "page": page,
                 "total_pages": paginator.num_pages,
                 },
                context_instance=RequestContext(request))

@login_required
def iknow_ajax_questions(request, 
                qtype="all",
                tribe_id=None, 
                tag_id=None, 
                template="iknow/iknow_ajax_questions.html"):
    home = False
    for_solved_questions = False
    if qtype.startswith("h_"):
        home = True
    if qtype == "all":
        questions = Question.objects.all()
        title = _("All questions")
    elif qtype == "active" or qtype == "h_active":
        title = _("Active questions in the marketplace")
        questions = Question.objects.filter(status__in=["A","E"])
    elif qtype == "solved" or qtype == "h_solved":
        title = _("Solved Questions")
        for_solved_questions = True
        questions = Question.objects.filter(status="S")
    elif qtype == "unanswered" or qtype == "h_unanswered":
        title = _("Questions ignored")
        questions = Question.objects.filter(status__in=["A","E"])
    elif qtype == "most_offered" or qtype == "h_most_offered":
        title = _("Most rewarding questions")
        questions = Question.objects.filter(status__in=["A", "E"], points_offered__gte=1)\
            .order_by("-points_offered")
    elif qtype == "my_favorite":
        return iknow_ajax_questions_fav(request, tribe_id, tag_id, template)
    else:
        questions = None
    if not tribe_id:
        questions = questions.filter(to_groups=None)
    else:
        tribe = Tribe.objects.get(pk=tribe_id)
        questions = questions.filter(to_groups=tribe)
    if tag_id:
        tag = QuestionTag.objects.get(pk=tag_id)
        title = _("Questions tagged with %(tag_name)s") % {"tag_name": tag.name}
        questions = questions.filter(tags__icontains=tag.name)
    if not questions:
        return render_to_response(template, 
                    {"objs": None,
                     "title": title,
                     "order": "time", 
                     "page": 0,
                     "total_pages": 0,
                     "qtype": qtype,
                     "home": home,
                     "for_solved_questions": for_solved_questions,
                     },
                    context_instance=RequestContext(request))
    order = "time"
    if qtype == "most_offered" or qtype == "h_most_offered":
        order = "points"
    page = 1
    if request.method == "GET":
        if request.GET.has_key("order"):
            order = request.GET["order"]
        if request.GET.has_key("page"):
            page = int(request.GET["page"])
    if order == "time":
        q_ordered = questions.order_by("-time_stamp")
    elif order == "points":
        q_ordered = questions.order_by("-points_offered")
    if qtype == "unanswered" or qtype == "h_unanswered":
        q_ordered = [obj for obj in q_ordered if obj.answer_set.count() == 0]
    paginator = Paginator(q_ordered, 40)
    return render_to_response(template, 
                {"objs":paginator.page(page),
                 "title": title,
                 "order": order, 
                 "page": page,
                 "total_pages": paginator.num_pages,
                 "qtype": qtype,
                 "home": home,
                 "for_solved_questions": for_solved_questions,
                 },
                context_instance=RequestContext(request))

# HTTP POST views
@login_required
def iknow_post_asker_hide(request):
    if request.method == "POST":
        try:
            question_id = request.POST["question_id"]
            question = Question.objects.get(pk=question_id)
            if question.asker != request.user:
                return HttpResponse("2")
            question.hide_answers = not question.hide_answers
            question.save()
            return HttpResponse("0")
        except Exception, e:
            klogger.warning(e)    
            return HttpResponse("1")

@login_required
def iknow_post_answerer_hide(request):
    if request.method == "POST":
        try:
            question_id = request.POST["question_id"]
            question = Question.objects.get(pk=question_id)
            answer = question.answer_set.filter(answerer=request.user)[0]
            answer.hidden = not answer.hidden
            answer.save()
            return HttpResponse("0")
        except Exception, e:
            klogger.warning(e)    
            return HttpResponse("1")

@login_required
def iknow_post_amendment(request):
    if request.method == "POST":
        try:
            question_id = request.POST["question_id"]
            amendment = request.POST["amendment"]
            question = Question.objects.get(pk=question_id)
            qa = QuestionAmendment (
                        question=question,
                        creator=request.user,
                        time_stamp=datetime.now(),
                        mp_code="QA",
                        details=amendment,
                        sharing=question.sharing,
                    )
            qa.save()
            return HttpResponse("0")
        except Exception, e:
            print e
            klogger.warning(e)    
            return HttpResponse("1")

@login_required
def iknow_post_add_favorite(request):
    if request.method == "POST":
        try:
            question_id = request.POST["question_id"]
            question = Question.objects.get(pk=question_id)
            get_egghead_from_user(request.user).add_question_as_favorite(question)
            return HttpResponse("0")
        except Exception, e:
            klogger.warning(e)    
            return HttpResponse("1")

@login_required
def iknow_thumbs(request):
    if request.method == "POST":
        try:
            ttype = request.POST.get("ttype", None)
        except IOError, e:
            klogger.warning("iknow_thumbs - ttype from POST: %s" % e)
            return HttpResponse("3")
        if not ttype:
            return HttpResponse("3")
        id = request.POST["id"]
        up_or_down = request.POST["up_or_down"]
        if ttype == "Q":
            question = Question.objects.get(pk=id)
            if question.asker == request.user:
                return HttpResponse("2")
            thumb, created = Thumb.objects.get_or_create(thumber=request.user, type="Q", 
                    question=question, defaults={"time_stamp": datetime.now()})
            if created:
                thumb.up_or_down = up_or_down
                thumb.save()
                if up_or_down == "U":
                    question.thumb_up = question.thumb_up + 1
                else:
                    question.thumb_down = question.thumb_down + 1
                question.save()
                question.update_thumbs()
                return HttpResponse("0")
            else:
                return HttpResponse("1")
        if ttype == "A":
            answer = Answer.objects.get(pk=id)
            if answer.answerer == request.user:
                return HttpResponse("2")
            thumb, created = Thumb.objects.get_or_create(thumber=request.user, type="A", 
                    answer=answer, defaults={"time_stamp": datetime.now()})
            if created:
                thumb.up_or_down = up_or_down
                thumb.question = answer.question
                thumb.save()
                if up_or_down == "U":
                    answer.thumb_up = answer.thumb_up + 1
                else:
                    answer.thumb_down = answer.thumb_down + 1
                answer.save()
                answer.update_thumbs()
                if worldbank_subsidize(request.user, "TU", answer.question) == 0:
                    return HttpResponse("8")
                else:
                    return HttpResponse("0")
            else:
                return HttpResponse("1")
    else: 
        return HttpResponse("This view only support post request")

@login_required
def iknow_comment(request):
    if request.method == "POST":
        try:
            comment = request.POST.get("comment", "")
        except IOError, e:
            klogger.warning("iknow_comment reading POST: %s" % e)
            return HttpResponse("1")
        cleaned_comment = comment.strip(" \n\t")    
        if not cleaned_comment:
            # error code 1, the comment itself is not valid
            return HttpResponse("1")
        ctype = request.POST["ctype"]
        anony = True
        if request.POST["anonymous"] == "false":
            anony = False
        if ctype == "A":
            try:
                answer_id = request.POST["answer_id"]
                answer = Answer.objects.get(pk=answer_id)
                ac = AnswerComment(answer=answer, creator=request.user, mp_code="AC",
                    time_stamp=datetime.now(), details=cleaned_comment, anonymous=anony)
                ac.save()

                recipients = set()
                recipients.add(answer.answerer)
                recipients.add(answer.question.asker)
                for comment in answer.answercomment_set.all():
                    recipients.add(comment.creator)
                current_site = Site.objects.get_current()
                # subject = "[ " + current_site.name + " ] " + "- Answer received a comment"
                subject = u"[ %s ] %s" % (current_site.name, _("An answer received a comment from %(commentor_name)s") % {
                        "commentor_name": core.utils.show_name(ac.creator)
                    })
                t = loader.get_template("iknow/new_comment.txt")
                c = Context({
                        "answer": answer,
                        "current_site": current_site,
                        "comment": ac,
                    })
                send_mail(subject, t.render(c), settings.DEFAULT_FROM_EMAIL, verified_emails(recipients))
                if AnswerComment.objects.filter(answer=answer, creator=request.user).count() == 1 \
                    and worldbank_subsidize(request.user, "AC", answer.question) == 0:
                    return HttpResponse("8")
                else:
                    return HttpResponse("0")
            except Exception, e:
                print e
                klogger.info(e)
                return HttpResponse("2")
        elif ctype == "Q":
            try:
                question_id = request.POST["question_id"]
                question = Question.objects.get(pk=question_id)
                qc = QuestionComment(question=question, creator=request.user, mp_code="QC",
                    time_stamp=datetime.now(), details=cleaned_comment, anonymous=anony)
                qc.save()
                recipients = set()
                recipients.add(question.asker)
                for comment in question.questioncomment_set.all():
                    recipients.add(comment.creator)
                current_site = Site.objects.get_current()
                # subject = "[ " + current_site.name + " ] " + "- Question received a comment"
                subject = u"[ %s ] %s" % (current_site.name, _("A question received a comment from %(commentor_name)s") % {
                        "commentor_name": core.utils.show_name(qc.creator)
                    })
                t = loader.get_template("iknow/question_new_comment.txt")
                c = Context({
                        "question": question,
                        "current_site": current_site,
                        "comment": qc,
                    })
                send_mail(subject, t.render(c), settings.DEFAULT_FROM_EMAIL, verified_emails(recipients))
                # TODO: reward for comments
                if QuestionComment.objects.filter(question=question, creator=request.user).count() == 1 \
                    and worldbank_subsidize(request.user, "KQC", question) == 0:
                    return HttpResponse("8")
                else:
                    return HttpResponse("0")
            except Exception, e:
                klogger.info(e)
                return HttpResponse("2")
    else:
        klogger.warning("iknow_comment received a non-POST request")

@login_required
def iknow_answerer_rating(request):
    if request.method == "POST":
        try:
            answer_id = request.POST["answer_id"]
            value = int(request.POST["value"])
            answer = Answer.objects.get(pk=answer_id)
            if answer.rating_by_asker == value:
                return HttpResponse("2") # Rated the same, shouldn't cause interface change
            else:
                answer.rating_by_asker = value
                answer.save()
                rating = Rating(rater=request.user, receiver=answer.answerer, rating=value,
                    question=answer.question, rtype="C", time_stamp=datetime.now())
                rating.save()
                return HttpResponse("0")
        except Exception, e:
            klogger.warning(e)
            return HttpResponse("1")

@login_required
def iknow_tipping(request):
    if request.method == "POST":
        try:
            
            answer_id = request.POST["id"]
            tip = int(request.POST["tip"])
            answer = Answer.objects.get(pk=answer_id)
            at = AnswerTip(answer=answer, tipper=request.user,
                time_stamp=datetime.now(), amount=tip)
            at.save()
            at.transfer()

            comment = request.POST["comment"]
            cleaned_comment = comment.strip(" \n\t")    
            if not cleaned_comment:
                cleaned_comment = _("Your answer is extremely helpful")
            ac = AnswerComment(answer=answer, creator=request.user, mp_code="AC",
                time_stamp=at.time_stamp, details=cleaned_comment, anonymous=False)
            ac.tip = at
            ac.save()

            recipients = (answer.answerer, )
            current_site = Site.objects.get_current()
            # subject = "[ " + current_site.name + " ] " + "- Your answer received tips"
            subject = u"[ %s ] %s" % (current_site.name, _("Your answer received %(tip_amount)d points tipping from %(tipper_name)s") % {
                    "tip_amount": at.amount,
                    "tipper_name": core.utils.show_name(at.tipper)
                })
            t = loader.get_template("iknow/answer_tips_received.txt")
            c = Context({
                    "answer": answer,
                    "current_site": current_site,
                    "tip": at,
                })
            send_mail(subject, t.render(c), settings.DEFAULT_FROM_EMAIL, verified_emails(recipients))

            return HttpResponse("0")
        except Exception, e:
            print e
            klogger.info(e)
    return HttpResponse("0")
            

@login_required
def iknow_ajax_suggested_questions(request, template="iknow/iknow_ajax_suggested_questions.html"):
    if request.method == "POST":
        keyword = request.POST.get("keyword", None)
        if keyword:
            try:
                results = search_questions(keyword)[:15]
                return render_to_response(template, 
                            {"results": results},
                            context_instance=RequestContext(request))
            except Exception, e:
                klogger.info(e)
                return HttpResponse("1")

@login_required
def iknow_dashboard(request, username, template="iknow/iknow_dashboard.html"):
    duser = User.objects.get(username=username)
    egghead = get_egghead_from_user(duser)
    return render_to_response(template, 
                {"duser": duser,
                 "egghead": egghead,},
                context_instance=RequestContext(request))

@login_required
def iknow_ajax_dashboard(request, username, dtype):
    duser = User.objects.get(username=username)
    egghead = get_egghead_from_user(duser)
    if dtype == "asked":
        if duser.id == request.user.id:
            my_questions = egghead.get_questions_asked(max_item=-1)
        else:
            my_questions = egghead.get_questions_asked(max_item=-1, purge_anonymous=True)
        title = _("Questions asked")
        template = "iknow/iknow_ajax_questions.html"
        qtype = "iasked"
        if not my_questions:
            return render_to_response(template, 
                        {"objs": None,
                         "title": title,
                         "order": "time", 
                         "page": 0,
                         "total_pages": 0,
                         "qtype": qtype,
                         "home": False,
                         "duser": duser,
                         },
                        context_instance=RequestContext(request))
        order = "time"
        page = 1
        if request.method == "POST":
            if request.POST.has_key("order"):
                order = request.POST["order"]
            if request.POST.has_key("page"):
                page = int(request.POST["page"])
        if order == "time":
            q_ordered = my_questions.order_by("-time_stamp")
        paginator = Paginator(q_ordered, 25)
        return render_to_response(template, 
                    {"objs":paginator.page(page),
                     "title": title,
                     "order": order, 
                     "page": page,
                     "total_pages": paginator.num_pages,
                     "qtype": qtype,
                     "home": False,
                     "duser": duser,
                     },
                    context_instance=RequestContext(request))

    elif dtype == "answered":
        try:
            if duser.id == request.user.id:
                my_answers = egghead.get_questions_answered(max_item=-1)
            else:
                my_answers = egghead.get_questions_answered(max_item=-1, purge_anonymous=True)
            return render_to_response("iknow/iknow_ajax_myanswers.html",
                    {"my_answers": my_answers,},
                    context_instance=RequestContext(request))
        except Exception, e:
            klogger.warning(e)
    
    elif dtype == "transaction":
        if duser.id != request.user.id and not request.user.is_staff and not request.user.is_superuser:
            return HttpResponse(_("You can not review others' transaction history"))
        freezecredits = FreezeCredit.objects.filter(fuser=duser, ftype="F", app="K", 
            cleared=False).order_by("-time_stamp")
        transactions = Transaction.objects.filter(Q(src=duser)|Q(dst=duser)).order_by("-time_stamp")
        return render_to_response("iknow/iknow_ajax_transaction.html",
                {"freezecredits": freezecredits,
                 "transactions": transactions,
                 "duser": duser,
                },
                context_instance=RequestContext(request))
        
# json views
@login_required
def iknow_json_answer_comments(request):
    if request.method == "GET":
        try:
            answer_id = request.GET["answer_id"]
            answer = Answer.objects.get(pk=answer_id)
            alist = []
            for comment in answer.comments():
                if comment.tip: 
                    tip_amount = comment.tip.amount
                else:
                    tip_amount = 0
                alist.append({
                    "id": comment.id,
                    "name": comment.display_name(),
                    "time": comment.time_string_l(),
                    "details": comment.details,
                    "tip": tip_amount,
                })
            json_string = simplejson.dumps(alist)
            return HttpResponse(json_string)
        except Exception, e:
            klogger.warning("iknow_json_answer_comments: %s: Comment: %s" % (e, comment.details))
            klogger.warning("iknow_json_answer_comments: the list: %s" % alist)
            return HttpResponse("1")

@login_required
def iknow_help(request, template="iknow/iknow_help.html"):

    return render_to_response(template, 
                {},
                context_instance=RequestContext(request))
