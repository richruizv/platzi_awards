import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls.base import reverse
from . models import Question

def create_question(question_text, days):
    """
    Create a question with the given question text, and publish the given number of days offset to now (negative for questions polish in the past)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text = question_text, pub_date = time )

# Create your tests here.
class QuestionModelTests(TestCase):
    
    def test_was_published_recently_with_future_questions(self):
        """
            was_published_recently returns false for question whose pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="How is the best course director of platzi?", pub_date=time)

        self.assertIs(future_question.was_published_recently(),False)
    

class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """If question no exists, an appropiate message is displayed"""

        response = self.client.get(reverse("polls:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_questions(self):
        """
        Questions with a problem in the future aren't displayed in the item page
        """

        create_question("future_question",days=30)
        response = self.client.get(reverse("polls:index"))

        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

        
    
    def test_past_future_questions(self):
        """
        Question with  a pub_date in the past are displayed in the future
        """
        question = create_question("past_question",days=-10)
        response = self.client.get(reverse("polls:index"))
        
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exists, only past questions are displayed
        """
        question_future = create_question(question_text="future_question" , days=30)
        question_past = create_question(question_text="past_question" , days=-10)

        response = self.client.get(reverse("polls:index"))

        self.assertQuerysetEqual(response.context["latest_question_list"], [question_past])
        
    def test_two_past_question(self):
        """
        Both question may display on index page
        """

        question_past1 = create_question(question_text="past_question1" , days=-30)
        question_past2 = create_question(question_text="past_question2" , days=-40)

        response = self.client.get(reverse("polls:index"))

        self.assertQuerysetEqual(response.context["latest_question_list"], [question_past1,question_past2])

class QuestionDetailViewTest(TestCase):

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future returns a 404 not found
        """

        question_future = create_question(question_text="future_question" , days=30)
        response = self.client.get(reverse("polls:detail" , args=(question_future.id,)))
        self.assertEqual(response.status_code, 404)

    def past_future_question(self):
        """
        The detail view of a question with a pub_date in the past  displays the question text
        """
        
        question_past = create_question(question_text="question_past" , days=-30)
        response = self.client.get(reverse("polls:detail"), args=(question_past.id,))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question_past.question_text)

class ResutlsViewTest(TestCase):

    def test_future_questions(self):
        """
        The result view of a question with a pub_date in the future returns a 404 not found
        """

        question_future = create_question(question_text="future_question" , days=30)
        response = self.client.get(reverse("polls:results" , args=(question_future.id,)))
        self.assertEqual(response.status_code, 404)



    def past_future_question(self):
        """
        The result view of a question with a pub_date in the past  displays the question text
        """
        
        question_past = create_question(question_text="question_past" , days=-30)
        response = self.client.get(reverse("polls:results"), args=(question_past.id,))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question_past.question_text)