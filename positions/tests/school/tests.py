from positions.tests.school.models import SubUnit, Lesson, Exercise
from django.test import TestCase
from unittest import skip

@skip
class TestParentLink(TestCase):
    def test_parent_link(self):
        american_revolution = SubUnit.objects.create(name="American Revolution")
        no_taxation = Lesson.objects.create(sub_unit=american_revolution, title="No Taxation without Representation", text="...")
        self.assertEqual(no_taxation.position, 0)
        research_paper = Exercise.objects.create(sub_unit=american_revolution, title="Paper", description="Two pages, double spaced")
        self.assertEqual(research_paper.position, 1)
        tea_party = Lesson.objects.create(sub_unit=american_revolution, title="Boston Tea Party", text="...")
        self.assertEqual(tea_party.position, 2)
        quiz = Exercise.objects.create(sub_unit=american_revolution, title="Pop Quiz", description="...")
        self.assertEqual(quiz.position, 3)
        # create a task with an explicit position
        Lesson.objects.create(sub_unit=american_revolution, title="The Intro", text="...", position=0)
        qs = american_revolution.task_set.order_by('position').values_list('title', 'position')
        self.assertQuerysetEqual(qs, [('The Intro', 0), ('No Taxation without Representation', 1), ('Paper', 2), ('Boston Tea Party', 3)],
                                 transform=tuple)
