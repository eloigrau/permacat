# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, reverse

from .forms import SuffrageForm, CommentaireSuffrageForm, CommentaireSuffrageChangeForm, SuffrageChangeForm, \
    VoteForm, VoteChangeForm, Question_majoritaire_Form, Question_binaire_formset, Proposition_m_formset, Reponse_binaire_Form, Reponse_majoritaire_Form

from formtools.wizard.views import SessionWizardView

FORMS = [("suffrage", SuffrageForm),
         ("question_b", Question_binaire_formset),
         ("question_m", Question_majoritaire_Form)]

TEMPLATES = {"suffrage": "vote/ajouterSuffrage.html",
             "question_b": "vote/ajouterQuestionB.html",
             "question_m": "vote/ajouterQuestionM.html",}

TEMPLATES = {"suffrage": "vote/suffrageWizard.html",
             "question_b": "vote/suffrageWizard.html",
             "question_m": "vote/suffrageWizard.html",}

class SuffrageWizard(SessionWizardView):
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        return HttpResponseRedirect('/page-to-redirect-to-when-done/')