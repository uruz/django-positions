from django.test import TestCase
from django.utils.unittest.case import skip
from positions.tests.photos.models import Album, Photo


@skip
class AlbumTestCase(TestCase):
    def setUp(self):
        self.album = Album.objects.create(name="Vacation")

    def test_zero_default(self):
        # The Photo model doesn't use the default (-1) position. Make sure that works.
        bahamas = self.album.photos.create(name="Bahamas")
        self.assertEqual(bahamas.position, 0)
        jamaica = self.album.photos.create(name="Jamaica")
        self.assertEqual(jamaica.position, 0)
        grand_cayman = self.album.photos.create(name="Grand Cayman")
        self.assertEqual(grand_cayman.position, 0)
        cozumel = self.album.photos.create(name="Cozumel")
        self.assertEqual(cozumel.position, 0)
        self.assertQuerysetEqual(self.album.photos.order_by('position').values_list('name', 'position'),
                                 [('Cozumel', 0), ('Grand Cayman', 1), ('Jamaica', 2), ('Bahamas', 3)],
                                 transform=tuple)

