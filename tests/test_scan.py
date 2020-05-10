import unittest
from unittest import mock

from django.test import TestCase

from vgloss import models, scan
from tests import testdata

class TestScan(TestCase):

    def setUp(self):
        testdata.basic_data()
        scan.scan_all()

    def tearDown(self):
        testdata.clean()

    def test_scan(self):
        black_square1 = models.FilePath.objects.get(path="black_square1.jpg")
        black_square2 = models.FilePath.objects.get(path="black_square2.jpg")
        black_square3 = models.FilePath.objects.get(path="dir1/black_square3.jpg")
        white_square = models.FilePath.objects.get(path="white_square.jpg")

        # Names and directories
        self.assertEqual(black_square1.folder, "")
        self.assertEqual(black_square1.filename, "black_square1.jpg")
        self.assertEqual(black_square2.folder, "")
        self.assertEqual(black_square2.filename, "black_square2.jpg")
        self.assertEqual(black_square3.folder, "dir1")
        self.assertEqual(black_square3.filename, "black_square3.jpg")
        self.assertEqual(white_square.folder, "")
        self.assertEqual(white_square.filename, "white_square.jpg")

        # File object equivalences
        self.assertEqual(black_square1.file, black_square2.file)
        self.assertEqual(black_square1.file, black_square3.file)
        self.assertNotEqual(black_square1.file, white_square.file)

        # File image metadata
        metadata = white_square.file.metadata
        self.assertEqual(metadata["BitsPerSample"], 8)
        self.assertEqual(metadata["ColorComponents"], 3)
        self.assertEqual(white_square.file.name, "white_square.jpg")
        self.assertTrue(white_square.file.is_image)

    def test_non_image_file(self):
        textfile = models.FilePath.objects.get(path="not_image.txt")
        self.assertEqual(textfile.file.mimetype, "text/plain")
        self.assertFalse(textfile.file.is_image)

    def test_versions(self):
        scan_version = scan.SCAN_VERSION

        # Scan version is set to constant
        self.assertSetEqual(
            set(models.File.objects.values_list("scan_version", flat=True)),
            {scan_version}
        )

        # No re-scan performed if SCAN_VERSION hasn't changed
        scan_file_mock = mock.Mock()
        with mock.patch("vgloss.scan.scan_file", scan_file_mock):
            scan.scan_all()
        scan_file_mock.assert_not_called()
        self.assertSetEqual(
            set(models.File.objects.values_list("scan_version", flat=True)),
            {scan_version}
        )

        # Re-scan if SCAN_VERSION updates
        with mock.patch("vgloss.scan.SCAN_VERSION", scan_version + 1):
            scan.scan_all()
        self.assertSetEqual(
            set(models.File.objects.values_list("scan_version", flat=True)),
            {scan_version + 1}
        )

    @unittest.skip("Test not implemented")
    def test_extract_timestamp(self):
        # From exif
        # From filename
        # From stat???
        raise NotImplementedError()

    @unittest.skip("Test not implemented")
    def test_image_types(self):
        # jpg, jpeg, png, gif, etc.
        raise NotImplementedError()

