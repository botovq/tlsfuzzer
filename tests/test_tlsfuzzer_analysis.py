# Author: Jan Koscielniak, (c) 2020
# Released under Gnu GPL v2.0, see LICENSE file for details
try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    import mock
except ImportError:
    import unittest.mock as mock

import sys

failed_import = False
try:
    from tlsfuzzer.analysis import Analysis, main, TestPair, help_msg
    import pandas as pd
except ImportError:
    failed_import = True


@unittest.skipIf(failed_import,
                 "Could not import analysis. Skipping related tests.")
class TestReport(unittest.TestCase):
    def setUp(self):
        data = {
            0: ["A", 0.000758130, 0.000696718, 0.000980080, 0.000988899, 0.000875510,
                0.000734843, 0.000754852, 0.000667378, 0.000671230, 0.000790935],
            1: ["B", 0.000758130, 0.000696718, 0.000980080, 0.000988899, 0.000875510,
                0.000734843, 0.000754852, 0.000667378, 0.000671230, 0.000790935],
            2: ["C", 0.000758130, 0.000696718, 0.000980080, 0.000988899, 0.000875510,
                0.000734843, 0.000754852, 0.000667378, 0.000671230, 0.000790935]
        }
        self.neq_data = {
            0: ["A", 0.000758130, 0.000696718, 0.000980080, 0.000988899, 0.000875510,
                0.000734843, 0.000754852, 0.000667378, 0.000671230, 0.000790935],
            1: ["B", 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        }
        self.neq_data_overlap = {
            0: ["A", 0, 0, 1, 7, 7] + [7] * 95,
            1: ["B", 0, 0, 2, 6, 7] + [7] * 95,
        }
        timings = pd.DataFrame(data=data)
        self.mock_read_csv = mock.Mock(spec=pd.read_csv)
        self.mock_read_csv.return_value = timings.transpose()

    def test_report(self):
        with mock.patch("tlsfuzzer.analysis.pd.read_csv", self.mock_read_csv):
            with mock.patch("tlsfuzzer.analysis.Analysis.qq_plot") as mock_qq:
                with mock.patch("tlsfuzzer.analysis.Analysis.ecdf_plot") as mock_ecdf:
                    with mock.patch("tlsfuzzer.analysis.Analysis.box_plot") as mock_box:
                        with mock.patch("tlsfuzzer.analysis.Analysis.scatter_plot") as mock_scatter:
                            with mock.patch("__main__.__builtins__.open", mock.mock_open()) as mock_open:
                                analysis = Analysis("/tmp")
                                ret = analysis.generate_report()

                                self.mock_read_csv.assert_called_once()
                                mock_qq.assert_called_once()
                                mock_ecdf.assert_called_once()
                                mock_box.assert_called_once()
                                mock_scatter.assert_called_once()
                                mock_open.assert_called_once()
                                self.assertEqual(ret, 0)

    def test_report_neq(self):
        timings = pd.DataFrame(data=self.neq_data)
        mock_read_csv = mock.Mock(spec=pd.read_csv)
        mock_read_csv.return_value = timings.transpose()
        with mock.patch("tlsfuzzer.analysis.pd.read_csv", mock_read_csv):
            with mock.patch("tlsfuzzer.analysis.Analysis.qq_plot") as mock_qq:
                with mock.patch("tlsfuzzer.analysis.Analysis.ecdf_plot") as mock_ecdf:
                    with mock.patch("tlsfuzzer.analysis.Analysis.box_plot") as mock_box:
                        with mock.patch("tlsfuzzer.analysis.Analysis.scatter_plot") as mock_scatter:
                            with mock.patch("__main__.__builtins__.open", mock.mock_open()) as mock_open:
                                analysis = Analysis("/tmp")
                                ret = analysis.generate_report()

                                mock_read_csv.assert_called_once()
                                mock_qq.assert_called_once()
                                mock_ecdf.assert_called_once()
                                mock_box.assert_called_once()
                                mock_scatter.assert_called_once()
                                mock_open.assert_called_once()
                                self.assertEqual(ret, 1)

    def test_ks_test(self):
        with mock.patch("tlsfuzzer.analysis.pd.read_csv", self.mock_read_csv):
            analysis = Analysis("/tmp")
            self.mock_read_csv.assert_called_once()

            res = analysis.ks_test()
            self.assertEqual(len(res), 3)
            for index, result in res.items():
                self.assertEqual(result, 1.0)

    def test_box_test(self):
        with mock.patch("tlsfuzzer.analysis.pd.read_csv", self.mock_read_csv):
            analysis = Analysis("/tmp")
            self.mock_read_csv.assert_called_once()

            res = analysis.box_test()
            self.assertEqual(len(res), 3)
            for index, result in res.items():
                self.assertEqual(result, None)

    def test_box_test_neq(self):
        timings = pd.DataFrame(data=self.neq_data)
        mock_read_csv = mock.Mock(spec=pd.read_csv)
        mock_read_csv.return_value = timings.transpose()
        with mock.patch("tlsfuzzer.analysis.pd.read_csv", mock_read_csv):
            analysis = Analysis("/tmp")

            res = analysis.box_test()
            self.assertEqual(len(res), 1)
            for index, result in res.items():
                self.assertNotEqual(result, None)

    def test_box_test_neq_overlap(self):
        timings = pd.DataFrame(data=self.neq_data_overlap)
        mock_read_csv = mock.Mock(spec=pd.read_csv)
        mock_read_csv.return_value = timings.transpose()
        with mock.patch("tlsfuzzer.analysis.pd.read_csv", mock_read_csv):
            analysis = Analysis("/tmp")
            mock_read_csv.assert_called_once()

            res = analysis.box_test()
            self.assertEqual(len(res), 1)
            for index, result in res.items():
                self.assertEqual(result, None)


@unittest.skipIf(failed_import,
                 "Could not import analysis. Skipping related tests.")
class TestPlots(unittest.TestCase):
    def setUp(self):
        data = {
            0: ["A", 0.000758130, 0.000696718, 0.000980080, 0.000988899, 0.000875510,
                0.000734843, 0.000754852, 0.000667378, 0.000671230, 0.000790935],
            1: ["B", 0.000758130, 0.000696718, 0.000980080, 0.000988899, 0.000875510,
                0.000734843, 0.000754852, 0.000667378, 0.000671230, 0.000790935]
        }
        timings = pd.DataFrame(data=data)
        mock_read_csv = mock.Mock(spec=pd.read_csv)
        mock_read_csv.return_value = timings.transpose()
        with mock.patch("tlsfuzzer.analysis.pd.read_csv", mock_read_csv):
            self.analysis = Analysis("/tmp")

    def test_qq_plot(self):
        with mock.patch("tlsfuzzer.analysis.plt.savefig", mock.Mock()) as mock_save:
            self.analysis.qq_plot()
            mock_save.assert_called_once()

    def test_ecdf_plot(self):
        with mock.patch("tlsfuzzer.analysis.plt.savefig", mock.Mock()) as mock_save:
            self.analysis.ecdf_plot()
            mock_save.assert_called_once()

    def test_scatter_plot(self):
        with mock.patch("tlsfuzzer.analysis.plt.savefig", mock.Mock()) as mock_save:
            self.analysis.scatter_plot()
            mock_save.assert_called_once()

    def test_box_plot(self):
        with mock.patch("tlsfuzzer.analysis.plt.savefig", mock.Mock()) as mock_save:
            self.analysis.box_plot()
            mock_save.assert_called_once()


@unittest.skipIf(failed_import,
                 "Could not import analysis. Skipping related tests.")
class TestCommandLine(unittest.TestCase):
    def test_command_line(self):
        output = "/tmp"
        args = ["analysis.py", "-o", output]
        mock_init = mock.Mock()
        mock_init.return_value = None
        with mock.patch('tlsfuzzer.analysis.Analysis.generate_report') as mock_report:
            with mock.patch('tlsfuzzer.analysis.Analysis.__init__', mock_init):
                with mock.patch("sys.argv", args):
                    main()
                    mock_report.assert_called_once()
                    mock_init.assert_called_once_with(output)

    def test_help(self):
        args = ["analysis.py", "--help"]
        with mock.patch('tlsfuzzer.analysis.help_msg') as help_mock:
            with mock.patch("sys.argv", args):
                self.assertRaises(SystemExit, main)
                help_mock.assert_called_once()

    def test_help_msg(self):
        with mock.patch('__main__.__builtins__.print') as print_mock:
            help_msg()
            self.assertGreaterEqual(print_mock.call_count, 1)

    def test_missing_output(self):
        args = ["analysis.py"]
        with mock.patch("sys.argv", args):
            self.assertRaises(ValueError, main)
