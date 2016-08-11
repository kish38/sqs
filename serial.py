from sqs.models import Quiz,Question
from sqs.serializers import QuizSerializer,QuestionSerializer

q = Quiz.objects.get(pk=4)
ss = QuizSerializer(q)
print ss.data
